# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.schema import normalize_notice
from core.text_utils import clean_text, extract_jalali_dates, in_jalali_range, jalali_canonical
from scrapers.base import ScrapeContext, fetch_html, new_session

BASE = "https://www.parsnamaddata.com"
PROVINCES = ["آذربایجان شرقی","آذربایجان غربی","اردبیل","اصفهان","البرز","ایلام","بوشهر","تهران","چهارمحال و بختیاری","خراسان جنوبی","خراسان رضوی","خراسان شمالی","خوزستان","زنجان","سمنان","سیستان و بلوچستان","فارس","قزوین","قم","کردستان","کرمان","کرمانشاه","کهگیلویه و بویراحمد","گلستان","گیلان","لرستان","مازندران","مرکزی","هرمزگان","همدان","یزد"]


def _url(kind: str, page: int) -> str:
    path = "tenders" if kind == "tender" else "inquiries"
    return f"{BASE}/{path}/page/{page}"


def _province(text: str) -> str:
    return next((p for p in PROVINCES if p in text), "")


def _parse(html: str, current_url: str, page: int, kind: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []
    seen = set()
    link_pattern = r"/(?:tender|inquiry)/(\d{4,})(?:/|$)"
    fallback_pattern = "مناقصه" if kind == "tender" else "استعلام"
    for a in soup.find_all("a", href=True):
        href = a.get("href") or ""
        text = clean_text(a.get_text(" ", strip=True))
        m = re.search(link_pattern, href)
        if not m and fallback_pattern not in text:
            continue
        code = m.group(1) if m else ""
        if not text or len(text) < 8:
            continue
        row_node = a.find_parent("tr") or a.find_parent(["article", "li", "section", "div"])
        raw = clean_text(row_node.get_text(" ", strip=True)) if row_node else text
        dates = extract_jalali_dates(raw)
        publish = dates[0] if dates else ""
        deadline = dates[-1] if len(dates) > 1 else ""
        key = code or urljoin(current_url, href) or text
        if key in seen:
            continue
        seen.add(key)
        rows.append(normalize_notice(
            id=f"parsnamad-{kind}-{code or page}-{len(rows)+1}",
            source="parsnamad",
            source_label="پارس‌نماد داده",
            notice_type=kind,
            notice_type_label="مناقصه" if kind == "tender" else "استعلام",
            code=code,
            title=text,
            employer="",
            province=_province(raw),
            city="",
            publish_date=jalali_canonical(publish),
            deadline=jalali_canonical(deadline),
            description=raw[:700],
            detail_url=urljoin(current_url, href),
            source_page=page,
            source_page_url=current_url,
            raw_text=raw[:1800],
        ))
    return rows


def scrape(kind: str, ctx: ScrapeContext) -> List[Dict]:
    session = new_session()
    out: List[Dict] = []
    empty_streak = 0
    for page in range(1, ctx.max_pages + 1):
        url = _url(kind, page)
        try:
            html = fetch_html(session, url, ctx)
        except Exception as exc:  # noqa: BLE001
            ctx.say(f"parsnamad {kind} page {page} failed: {repr(exc)}")
            empty_streak += 1
            if empty_streak >= 3:
                break
            continue
        parsed = _parse(html, url, page, kind)
        ctx.say(f"parsnamad {kind} page {page}: parsed={len(parsed)}")
        if not parsed:
            empty_streak += 1
            if empty_streak >= 3:
                break
            continue
        empty_streak = 0
        in_range_rows = []
        older_seen = False
        for row in parsed:
            date_value = row.get("publish_date") or row.get("deadline")
            if date_value and in_jalali_range(date_value, ctx.from_date, ctx.to_date):
                in_range_rows.append(row)
            elif date_value and date_value < jalali_canonical(ctx.from_date):
                older_seen = True
        out.extend(in_range_rows)
        ctx.say(f"parsnamad {kind} page {page}: in_range={len(in_range_rows)} total={len(out)}")
        if older_seen and not in_range_rows:
            ctx.say("parsnamad stop: older page reached")
            break
    return out
