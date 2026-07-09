# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.schema import normalize_notice
from core.text_utils import clean_text, extract_jalali_dates, in_jalali_range, jalali_canonical, jalali_dash
from scrapers.base import ScrapeContext, fetch_html, new_session

BASE = "https://www.hezarehinfo.net"


def _candidate_urls(kind: str, page: int, ctx: ScrapeContext) -> list[str]:
    path = "tenders" if kind == "tender" else "inquiries"
    # The site changes URL patterns periodically. Keep safe fallbacks.
    return [
        f"{BASE}/{path}/-!/pfrom-{jalali_dash(ctx.from_date)}/pto-{jalali_dash(ctx.to_date)}/page-{page:02d}",
        f"{BASE}/{path}/-!/pfrom-{jalali_dash(ctx.from_date)}/pto-{jalali_dash(ctx.to_date)}/page-{page}",
        f"{BASE}/{path}/-!/page-{page}",
        f"{BASE}/{path}/-!/page-{page:02d}",
    ]


def _parse(html: str, current_url: str, page: int, kind: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []
    seen = set()
    persian_type = "مناقصه" if kind == "tender" else "استعلام"
    for node in soup.find_all(["article", "li", "tr", "div"]):
        raw = clean_text(node.get_text(" ", strip=True))
        if len(raw) < 25 or persian_type not in raw and ("مشاوره" not in raw and "طراحی" not in raw and "مطالعات" not in raw):
            continue
        a = node.find("a", href=True)
        if not a:
            continue
        title = clean_text(a.get_text(" ", strip=True)) or raw[:150]
        href = a.get("href") or ""
        dates = extract_jalali_dates(raw)
        publish = dates[0] if dates else ""
        deadline = dates[-1] if len(dates) > 1 else ""
        code_match = re.search(r"(?:شماره|کد)\s*[:：]?\s*([0-9]{4,})", raw)
        code = code_match.group(1) if code_match else ""
        key = code or urljoin(current_url, href) or title
        if key in seen:
            continue
        seen.add(key)
        rows.append(normalize_notice(
            id=f"hezareh-{kind}-{code or page}-{len(rows)+1}",
            source="hezareh",
            source_label="هزاره",
            notice_type=kind,
            notice_type_label="مناقصه" if kind == "tender" else "استعلام",
            code=code,
            title=title,
            employer="",
            province="",
            city="",
            publish_date=jalali_canonical(publish),
            deadline=jalali_canonical(deadline),
            description=raw[:700],
            detail_url=urljoin(current_url, href),
            source_page=page,
            source_page_url=current_url,
            raw_text=raw[:1800],
        ))
    # Fallback: scan anchors if card parsing returns nothing.
    if not rows:
        for a in soup.find_all("a", href=True):
            title = clean_text(a.get_text(" ", strip=True))
            href = a.get("href") or ""
            if len(title) < 12:
                continue
            if not any(term in title for term in ["مناقصه", "استعلام", "مشاوره", "طراحی", "مطالعات", "نظارت"]):
                continue
            rows.append(normalize_notice(
                id=f"hezareh-{kind}-fallback-{page}-{len(rows)+1}",
                source="hezareh",
                source_label="هزاره",
                notice_type=kind,
                notice_type_label="مناقصه" if kind == "tender" else "استعلام",
                title=title,
                detail_url=urljoin(current_url, href),
                source_page=page,
                source_page_url=current_url,
                raw_text=title,
            ))
    return rows


def scrape(kind: str, ctx: ScrapeContext) -> List[Dict]:
    session = new_session()
    out: List[Dict] = []
    empty_streak = 0
    for page in range(1, ctx.max_pages + 1):
        html = ""
        used_url = ""
        for url in _candidate_urls(kind, page, ctx):
            try:
                html = fetch_html(session, url, ctx)
                used_url = url
                if html:
                    break
            except Exception as exc:  # noqa: BLE001
                ctx.say(f"hezareh try failed {url}: {repr(exc)}")
        if not html:
            empty_streak += 1
            if empty_streak >= 3:
                break
            continue
        parsed = _parse(html, used_url, page, kind)
        ctx.say(f"hezareh {kind} page {page}: parsed={len(parsed)}")
        if not parsed:
            empty_streak += 1
            if empty_streak >= 3:
                break
            continue
        empty_streak = 0
        in_range_rows = []
        has_dates = False
        older_seen = False
        for row in parsed:
            date_value = row.get("publish_date") or row.get("deadline")
            if date_value:
                has_dates = True
                if in_jalali_range(date_value, ctx.from_date, ctx.to_date):
                    in_range_rows.append(row)
                elif date_value < jalali_canonical(ctx.from_date):
                    older_seen = True
            else:
                # If date is missing, keep item for AI review but mark risk through raw data.
                in_range_rows.append(row)
        out.extend(in_range_rows)
        ctx.say(f"hezareh {kind} page {page}: in_range_or_no_date={len(in_range_rows)} total={len(out)}")
        if has_dates and older_seen and not in_range_rows:
            ctx.say("hezareh stop: older page reached")
            break
    return out
