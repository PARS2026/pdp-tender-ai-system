# -*- coding: utf-8 -*-
"""Normalized notice schema helpers."""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict

NORMALIZED_FIELDS = [
    "id", "source", "source_label", "notice_type", "notice_type_label",
    "code", "title", "employer", "province", "city", "publish_date",
    "deadline", "description", "detail_url", "all_links", "source_page",
    "source_page_url", "raw_text", "scraped_at_utc"
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def empty_notice() -> Dict[str, Any]:
    return {field: "" for field in NORMALIZED_FIELDS} | {"all_links": []}


def normalize_notice(**kwargs: Any) -> Dict[str, Any]:
    row = empty_notice()
    row.update({k: v for k, v in kwargs.items() if k in row})
    if not row.get("all_links") and row.get("detail_url"):
        row["all_links"] = [row["detail_url"]]
    if not row.get("scraped_at_utc"):
        row["scraped_at_utc"] = now_utc()
    return row
