# -*- coding: utf-8 -*-
from __future__ import annotations

from difflib import SequenceMatcher
from typing import Dict, List

from .text_utils import make_stable_key, normalize_persian


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate_notices(rows: List[Dict]) -> List[Dict]:
    """Merge likely duplicate notices across sources.

    Exact code/detail_url duplicates are merged first. Then title/employer/date similarity
    is used conservatively. All links are preserved in `all_links`.
    """
    merged: List[Dict] = []
    code_index: Dict[str, Dict] = {}
    url_index: Dict[str, Dict] = {}

    def absorb(target: Dict, src: Dict) -> None:
        links = list(target.get("all_links") or [])
        for link in [src.get("detail_url"), *(src.get("all_links") or [])]:
            if link and link not in links:
                links.append(link)
        target["all_links"] = links
        sources = set(str(target.get("source", "")).split("+")) | set(str(src.get("source", "")).split("+"))
        target["source"] = "+".join(sorted(s for s in sources if s))
        labels = set(str(target.get("source_label", "")).split("+")) | set(str(src.get("source_label", "")).split("+"))
        target["source_label"] = "+".join(sorted(s for s in labels if s))
        for key in ["employer", "province", "city", "deadline", "publish_date", "description", "raw_text"]:
            if not target.get(key) and src.get(key):
                target[key] = src[key]

    for row in rows:
        code_key = make_stable_key(row.get("source"), row.get("notice_type"), row.get("code")) if row.get("code") else ""
        url_key = row.get("detail_url") or ""
        target = None
        if code_key and code_key in code_index:
            target = code_index[code_key]
        elif url_key and url_key in url_index:
            target = url_index[url_key]
        else:
            title_key = normalize_persian(row.get("title"))
            emp_key = normalize_persian(row.get("employer"))
            date_key = row.get("publish_date") or row.get("deadline") or ""
            for old in merged:
                if old.get("notice_type") != row.get("notice_type"):
                    continue
                old_title = normalize_persian(old.get("title"))
                old_emp = normalize_persian(old.get("employer"))
                old_date = old.get("publish_date") or old.get("deadline") or ""
                if date_key and old_date and date_key != old_date:
                    continue
                if title_key and old_title and _similar(title_key, old_title) >= 0.91:
                    if not emp_key or not old_emp or _similar(emp_key, old_emp) >= 0.80:
                        target = old
                        break
        if target:
            absorb(target, row)
            continue
        new_row = dict(row)
        if not new_row.get("all_links") and new_row.get("detail_url"):
            new_row["all_links"] = [new_row["detail_url"]]
        merged.append(new_row)
        if code_key:
            code_index[code_key] = new_row
        if url_key:
            url_index[url_key] = new_row

    for i, row in enumerate(merged, start=1):
        if not row.get("id"):
            row["id"] = f"notice-{i:06d}"
    return merged
