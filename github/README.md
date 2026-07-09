# GitHub side - PDP Tender AI System

این پوشه باید در ریشه Repository گیت‌هاب قرار بگیرد. ساختار نهایی بعد از کپی باید به شکل زیر باشد:

```text
.github/workflows/pdp_tender_scrape.yml
requirements.txt
scripts/pdp_scrape.py
scripts/core/...
scripts/scrapers/...
outputs/            # بعد از اجرای workflow ساخته می‌شود
```

## اجرای دستی در GitHub

از تب **Actions**، workflow با نام **PDP Tender Scrape** را اجرا کنید و این ورودی‌ها را بدهید:

- `from_date`: تاریخ شروع جلالی مثل `1405-04-16`
- `to_date`: تاریخ پایان جلالی مثل `1405-04-17`
- `sources`: منابع فعال، مثل:
  `hezareh_tenders,hezareh_inquiries,parsnamad_tenders,parsnamad_inquiries`
- `max_pages`: سقف صفحات هر منبع

## خروجی‌ها

بعد از اجرای موفق، این فایل‌ها در پوشه `outputs` ساخته و commit می‌شوند:

- `pdp_normalized_latest.json`  ← ورودی اصلی برای Apps Script و OpenAI
- `pdp_raw_latest.json`         ← داده خام برای عیب‌یابی
- `pdp_normalized_latest.csv`
- `pdp_normalized_latest.xlsx`
- `pdp_tenders_latest.xlsx`
- `pdp_inquiries_latest.xlsx`
- `pdp_summary_latest.json`
- `pdp_scrape_log.txt`

## افزودن سایت جدید

برای سایت جدید، یک فایل جدید در `scripts/scrapers/` بسازید و آن را در `SOURCE_MAP` داخل `scripts/pdp_scrape.py` ثبت کنید. خروجی هر scraper باید به قالب استاندارد `normalize_notice(...)` تبدیل شود.
