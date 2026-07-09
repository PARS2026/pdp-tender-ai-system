#!/usr/bin/env python3
"""Fetch ChatGPT Scheduled analysis JSON from a Google Doc and build a static site.

Input: Google Doc ID whose content is valid JSON.
Output: public/ static GitHub Pages site and copied JSON data.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, re.S | re.I)
    if m:
        return m.group(1).strip()
    return stripped


def fetch_google_doc_text(doc_id: str, timeout: int = 30) -> str:
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    req = urllib.request.Request(url, headers={"User-Agent": "PDP-GitHub-Pages-Prototype/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"Could not fetch Google Doc export. HTTP {e.code}. "
            "For this prototype, share the Google Doc as 'Anyone with the link can view', "
            "or use a Drive credential-based workflow in the final version."
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not fetch Google Doc export: {e}") from e
    return data.decode("utf-8", errors="replace")


def read_sample_analysis(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_analysis(text: str) -> Dict[str, Any]:
    cleaned = strip_code_fence(text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        preview = cleaned[:500].replace("\n", " ")
        raise RuntimeError(f"Drive document content is not valid JSON. Preview: {preview}") from e
    if not isinstance(data, dict):
        raise RuntimeError("Analysis JSON must be an object at the top level.")
    return data


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def normalized_items(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "suggested_tenders": list(data.get("suggested_tenders") or []),
        "suggested_inquiries": list(data.get("suggested_inquiries") or []),
        "rejected_items": list(data.get("rejected_items") or []),
    }


def render_cards(items: List[Dict[str, Any]], empty_text: str) -> str:
    if not items:
        return f'<div class="empty">{esc(empty_text)}</div>'
    cards = []
    for item in items:
        title = esc(item.get("title"))
        employer = esc(item.get("employer"))
        category = esc(item.get("category"))
        importance = esc(item.get("importance"))
        urgency = esc(item.get("urgency"))
        score = esc(item.get("score"))
        reason = esc(item.get("reason"))
        action = esc(item.get("recommended_action"))
        risk = esc(item.get("risk_notes"))
        source = esc(item.get("source") or item.get("source_label"))
        url = item.get("source_url") or item.get("url") or ""
        link_html = f'<a href="{esc(url)}" target="_blank" rel="noopener">لینک منبع</a>' if url else ""
        cards.append(f"""
        <article class="card" data-search="{title} {employer} {category} {source}">
          <div class="card-head">
            <h3>{title}</h3>
            <div class="badges">
              <span>اهمیت: {importance or '-'}</span>
              <span>فوریت: {urgency or '-'}</span>
              <span>امتیاز: {score or '-'}</span>
            </div>
          </div>
          <div class="meta">کارفرما: {employer or '-'} | رشته/دسته: {category or '-'} | منبع: {source or '-'}</div>
          <p><strong>دلیل انتخاب:</strong> {reason or '-'}</p>
          <p><strong>اقدام پیشنهادی:</strong> {action or '-'}</p>
          <p><strong>ریسک/یادداشت:</strong> {risk or '-'}</p>
          <div class="links">{link_html}</div>
        </article>
        """)
    return "\n".join(cards)


def render_rejected(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<div class="empty">مورد ردشده‌ای ثبت نشده است.</div>'
    rows = []
    for item in items:
        rows.append(f"<tr><td>{esc(item.get('id'))}</td><td>{esc(item.get('title'))}</td><td>{esc(item.get('reason'))}</td></tr>")
    return f"""
    <div class="table-wrap"><table>
      <thead><tr><th>شناسه</th><th>عنوان</th><th>علت رد</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    """


def dashboard_html(data: Dict[str, Any], lists: Dict[str, List[Dict[str, Any]]]) -> str:
    dashboard = data.get("dashboard") or {}
    total = dashboard.get("total_input_items", "-")
    tenders = dashboard.get("suggested_tenders_count", len(lists["suggested_tenders"]))
    inquiries = dashboard.get("suggested_inquiries_count", len(lists["suggested_inquiries"]))
    urgent = dashboard.get("urgent_count", "-")
    rejected = len(lists["rejected_items"])
    return f"""
    <section class="stats">
      <div class="stat"><span>کل ورودی</span><b>{esc(total)}</b></div>
      <div class="stat"><span>مناقصات پیشنهادی</span><b>{esc(tenders)}</b></div>
      <div class="stat"><span>استعلامات پیشنهادی</span><b>{esc(inquiries)}</b></div>
      <div class="stat"><span>فوری</span><b>{esc(urgent)}</b></div>
      <div class="stat"><span>ردشده</span><b>{esc(rejected)}</b></div>
    </section>
    """


def build_site(data: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "data" / "analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lists = normalized_items(data)
    generated_at = esc(data.get("generated_at"))
    notes = data.get("notes") or data.get("analysis_notes") or []
    notes_html = "".join(f"<li>{esc(n)}</li>" for n in notes) if isinstance(notes, list) else esc(notes)

    html_text = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>سامانه پایش مناقصات PDP - Prototype</title>
  <style>
    :root {{ --bg:#f6f7fb; --card:#fff; --ink:#14213d; --muted:#667085; --brand:#003459; --accent:#0077b6; --ok:#087f5b; --warn:#b54708; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Tahoma, Arial, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:linear-gradient(135deg,var(--brand),#001d3d); color:white; padding:28px 24px; }}
    header h1 {{ margin:0 0 8px; font-size:24px; }}
    header p {{ margin:0; color:#d8e7f1; }}
    main {{ max-width:1200px; margin:24px auto; padding:0 16px; }}
    .toolbar {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom:18px; }}
    .search {{ flex:1; min-width:240px; padding:12px 14px; border:1px solid #d0d5dd; border-radius:12px; font-size:14px; }}
    .tabs {{ display:flex; gap:8px; flex-wrap:wrap; margin:18px 0; }}
    .tab {{ border:0; border-radius:999px; padding:10px 16px; background:#e6eef5; color:var(--brand); cursor:pointer; font-weight:bold; }}
    .tab.active {{ background:var(--brand); color:white; }}
    .panel {{ display:none; }}
    .panel.active {{ display:block; }}
    .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:18px; }}
    .stat {{ background:var(--card); border:1px solid #e4e7ec; border-radius:16px; padding:18px; box-shadow:0 1px 2px rgba(16,24,40,.05); }}
    .stat span {{ display:block; color:var(--muted); font-size:13px; }}
    .stat b {{ display:block; margin-top:8px; font-size:26px; color:var(--brand); }}
    .card {{ background:var(--card); border:1px solid #e4e7ec; border-radius:18px; padding:18px; margin:12px 0; box-shadow:0 1px 2px rgba(16,24,40,.06); }}
    .card-head {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; flex-wrap:wrap; }}
    h2 {{ margin-top:24px; }}
    h3 {{ margin:0; font-size:18px; }}
    .badges {{ display:flex; gap:6px; flex-wrap:wrap; }}
    .badges span {{ background:#eef6ff; color:#175cd3; border-radius:999px; padding:5px 9px; font-size:12px; }}
    .meta {{ color:var(--muted); margin:10px 0; font-size:13px; }}
    a {{ color:var(--accent); text-decoration:none; font-weight:bold; }}
    .empty {{ background:var(--card); border:1px dashed #cbd5e1; border-radius:16px; padding:24px; color:var(--muted); text-align:center; }}
    .table-wrap {{ overflow:auto; background:white; border-radius:16px; border:1px solid #e4e7ec; }}
    table {{ width:100%; border-collapse:collapse; min-width:700px; }}
    th, td {{ padding:12px; border-bottom:1px solid #e4e7ec; text-align:right; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    footer {{ text-align:center; color:var(--muted); padding:28px; }}
    .note {{ background:#fff7ed; border:1px solid #fed7aa; border-radius:16px; padding:14px 18px; margin:12px 0; color:#7c2d12; }}
  </style>
</head>
<body>
  <header>
    <h1>سامانه پایش مناقصات و استعلامات PDP - نمونه اولیه</h1>
    <p>استخراج در GitHub، تحلیل با ChatGPT Scheduled، برگشت خروجی از Google Drive، انتشار با GitHub Pages</p>
  </header>
  <main>
    <div class="note">آخرین تحلیل: {generated_at or '-'}</div>
    {dashboard_html(data, lists)}
    <div class="toolbar">
      <input class="search" id="search" placeholder="جستجو در عنوان، کارفرما، رشته و منبع..." />
      <a href="data/analysis.json" download>دانلود JSON تحلیل</a>
    </div>
    <div class="tabs">
      <button class="tab active" data-tab="dashboard">داشبورد</button>
      <button class="tab" data-tab="tenders">مناقصات پیشنهادی</button>
      <button class="tab" data-tab="inquiries">استعلامات پیشنهادی</button>
      <button class="tab" data-tab="rejected">ردشده‌ها</button>
      <button class="tab" data-tab="notes">یادداشت‌ها</button>
    </div>
    <section id="dashboard" class="panel active">
      <h2>خلاصه</h2>
      <div class="card"><pre>{esc(json.dumps(data.get('dashboard') or {{}}, ensure_ascii=False, indent=2))}</pre></div>
    </section>
    <section id="tenders" class="panel">
      <h2>مناقصات پیشنهادی</h2>
      {render_cards(lists['suggested_tenders'], 'مناقصه پیشنهادی وجود ندارد.')}
    </section>
    <section id="inquiries" class="panel">
      <h2>استعلامات پیشنهادی</h2>
      {render_cards(lists['suggested_inquiries'], 'استعلام پیشنهادی وجود ندارد.')}
    </section>
    <section id="rejected" class="panel">
      <h2>موارد ردشده</h2>
      {render_rejected(lists['rejected_items'])}
    </section>
    <section id="notes" class="panel">
      <h2>یادداشت‌های تحلیل</h2>
      <div class="card"><ul>{notes_html}</ul></div>
    </section>
  </main>
  <footer>Prototype v0.1 - بدون Apps Script و بدون OpenAI API</footer>
  <script>
    document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => {{
      document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');
    }}));
    document.getElementById('search').addEventListener('input', (e) => {{
      const q = e.target.value.trim().toLowerCase();
      document.querySelectorAll('.card[data-search]').forEach(card => {{
        const hay = card.dataset.search.toLowerCase();
        card.style.display = !q || hay.includes(q) ? '' : 'none';
      }});
    }});
  </script>
</body>
</html>
"""
    (out_dir / "index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-id", default="", help="Google Doc ID containing valid JSON analysis")
    parser.add_argument("--sample", action="store_true", help="Use sample_drive_output JSON instead of Google Drive")
    parser.add_argument("--sample-path", default="sample_drive_output/pdp_ai_analysis_latest.json")
    parser.add_argument("--out-dir", default="public")
    args = parser.parse_args()

    if args.sample:
        data = read_sample_analysis(Path(args.sample_path))
    else:
        if not args.doc_id:
            raise SystemExit("--doc-id is required unless --sample is used")
        text = fetch_google_doc_text(args.doc_id)
        data = parse_analysis(text)

    data.setdefault("site_built_at", now_iso())
    build_site(data, Path(args.out_dir))
    print(f"Built site in {args.out_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
