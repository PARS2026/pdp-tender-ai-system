#!/usr/bin/env python3
"""Lightweight extraction simulator for PDP GitHub + Scheduled + Drive prototype.

This script intentionally does not call OpenAI and does not use Google Apps Script.
It creates a small normalized JSON file that ChatGPT Scheduled can read from GitHub.
Later, this script can be replaced by the real tender scrapers.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_items(from_date: str, to_date: str) -> List[Dict[str, Any]]:
    return [
        {
            "id": "sample-tender-001",
            "notice_type": "tender",
            "title": "انتخاب مشاور برای مطالعات ماده 23 و طراحی ساختمان اداری",
            "employer": "اداره کل نمونه",
            "source": "sample_hezareh_tenders",
            "source_label": "نمونه هزاره - مناقصات",
            "source_url": "https://example.com/tender/sample-001",
            "all_links": ["https://example.com/tender/sample-001"],
            "province": "تهران",
            "publish_date": from_date,
            "deadline_date": to_date,
            "description": "خدمات مشاوره شامل مطالعات پایه، ماده 23، طراحی معماری، سازه و تأسیسات ساختمان اداری.",
            "raw_text": "انتخاب مشاور برای مطالعات ماده 23 و طراحی ساختمان اداری - خدمات مهندسین مشاور",
        },
        {
            "id": "sample-inquiry-001",
            "notice_type": "inquiry",
            "title": "استعلام خدمات نظارت عالیه و کارگاهی پروژه عمرانی",
            "employer": "شهرداری نمونه",
            "source": "sample_parsnamad_inquiries",
            "source_label": "نمونه پارس نماد - استعلامات",
            "source_url": "https://example.com/inquiry/sample-001",
            "all_links": ["https://example.com/inquiry/sample-001"],
            "province": "کرمان",
            "publish_date": from_date,
            "deadline_date": to_date,
            "description": "استعلام خدمات مهندسین مشاور برای نظارت عالیه و کارگاهی پروژه عمرانی شهری.",
            "raw_text": "استعلام خدمات نظارت عالیه و کارگاهی پروژه عمرانی شهری",
        },
        {
            "id": "sample-reject-001",
            "notice_type": "tender",
            "title": "خرید لوازم مصرفی و تجهیزات اداری",
            "employer": "شرکت نمونه",
            "source": "sample_hezareh_tenders",
            "source_label": "نمونه هزاره - مناقصات",
            "source_url": "https://example.com/tender/sample-002",
            "all_links": ["https://example.com/tender/sample-002"],
            "province": "تهران",
            "publish_date": from_date,
            "deadline_date": to_date,
            "description": "خرید کالا و لوازم مصرفی بدون خدمات مشاوره، طراحی یا نظارت.",
            "raw_text": "خرید لوازم مصرفی و تجهیزات اداری",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default="1405-04-18")
    parser.add_argument("--to-date", default="1405-04-19")
    parser.add_argument("--out-dir", default="outputs")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = build_items(args.from_date, args.to_date)
    normalized = {
        "schema_version": "pdp-normalized-test-v1",
        "generated_at": now_iso(),
        "mode": "lightweight_prototype_sample_extract",
        "from_date": args.from_date,
        "to_date": args.to_date,
        "item_count": len(items),
        "items": items,
        "instructions_for_scheduled": {
            "purpose": "ChatGPT Scheduled should read this file, analyze PDP relevance, and write valid analysis JSON to Google Drive.",
            "do_not_use_openai_api": True,
            "do_not_use_apps_script": True,
        },
    }

    summary = {
        "generated_at": normalized["generated_at"],
        "item_count": len(items),
        "tenders": sum(1 for i in items if i["notice_type"] == "tender"),
        "inquiries": sum(1 for i in items if i["notice_type"] == "inquiry"),
        "next_step": "Run ChatGPT Scheduled analysis and write result to Google Drive.",
    }

    (out_dir / "pdp_normalized_latest.json").write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "pdp_summary_latest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_dir / 'pdp_normalized_latest.json'}")
    print(f"Wrote {out_dir / 'pdp_summary_latest.json'}")


if __name__ == "__main__":
    main()
