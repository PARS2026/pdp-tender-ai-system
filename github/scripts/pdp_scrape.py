# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from typing import Dict, List

# Allow running as a script from repository root or scripts folder.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core.deduplicate import deduplicate_notices
from core.export_outputs import ensure_dir, write_json, write_tabular
from scrapers.base import ScrapeContext
from scrapers import hezareh, parsnamad

SOURCE_MAP = {
    "hezareh_tenders": (hezareh.scrape, "tender"),
    "hezareh_inquiries": (hezareh.scrape, "inquiry"),
    "parsnamad_tenders": (parsnamad.scrape, "tender"),
    "parsnamad_inquiries": (parsnamad.scrape, "inquiry"),
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="PDP tender/inquiry scraper")
    parser.add_argument("--from-date", required=True, help="Jalali date, e.g. 1405-04-16 or 1405/04/16")
    parser.add_argument("--to-date", required=True, help="Jalali date, e.g. 1405-04-17 or 1405/04/17")
    parser.add_argument("--sources", default=",".join(SOURCE_MAP), help="Comma-separated source keys")
    parser.add_argument("--max-pages", type=int, default=60)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--out-dir", default="outputs")
    args = parser.parse_args()

    ensure_dir(args.out_dir)
    log_path = os.path.join(args.out_dir, "pdp_scrape_log.txt")
    open(log_path, "w", encoding="utf-8").close()

    def log(msg: str) -> None:
        line = f"[{utc_now()}] {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    selected = [s.strip() for s in args.sources.split(",") if s.strip()]
    unknown = [s for s in selected if s not in SOURCE_MAP]
    if unknown:
        raise SystemExit(f"Unknown sources: {unknown}. Valid sources: {sorted(SOURCE_MAP)}")

    raw_rows: List[Dict] = []
    source_stats: Dict[str, int] = {}
    ctx = ScrapeContext(
        from_date=args.from_date,
        to_date=args.to_date,
        max_pages=args.max_pages,
        delay_seconds=args.delay_seconds,
        retries=args.retries,
        log=log,
    )

    for source_key in selected:
        scrape_func, kind = SOURCE_MAP[source_key]
        log(f"START source={source_key} kind={kind}")
        try:
            rows = scrape_func(kind, ctx)
        except Exception as exc:  # noqa: BLE001
            log(f"SOURCE ERROR {source_key}: {repr(exc)}")
            rows = []
        source_stats[source_key] = len(rows)
        raw_rows.extend(rows)
        log(f"DONE source={source_key} rows={len(rows)}")

    normalized = deduplicate_notices(raw_rows)
    payload = {
        "schemaVersion": "pdp-normalized-v1",
        "generatedAtUtc": utc_now(),
        "fromDate": args.from_date,
        "toDate": args.to_date,
        "sources": selected,
        "sourceStats": source_stats,
        "totalRawRows": len(raw_rows),
        "totalNormalizedRows": len(normalized),
        "items": normalized,
    }
    write_json(os.path.join(args.out_dir, "pdp_raw_latest.json"), {"items": raw_rows, "generatedAtUtc": utc_now()})
    write_json(os.path.join(args.out_dir, "pdp_normalized_latest.json"), payload)
    write_tabular(os.path.join(args.out_dir, "pdp_normalized_latest"), normalized)

    tenders = [r for r in normalized if r.get("notice_type") == "tender"]
    inquiries = [r for r in normalized if r.get("notice_type") == "inquiry"]
    write_tabular(os.path.join(args.out_dir, "pdp_tenders_latest"), tenders)
    write_tabular(os.path.join(args.out_dir, "pdp_inquiries_latest"), inquiries)

    summary = {
        "generatedAtUtc": utc_now(),
        "sourceStats": source_stats,
        "totalRawRows": len(raw_rows),
        "totalNormalizedRows": len(normalized),
        "tenders": len(tenders),
        "inquiries": len(inquiries),
    }
    write_json(os.path.join(args.out_dir, "pdp_summary_latest.json"), summary)
    log("SUMMARY " + json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
