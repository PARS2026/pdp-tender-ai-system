# PDP GitHub + Drive + Scheduled Prototype v0.1

این بسته یک نمونه اولیه سبک برای تست معماری جدید سامانه پایش مناقصات PDP است:

```text
بدون Google Apps Script
بدون OpenAI API
استخراج/ساخت خروجی در GitHub Actions
تحلیل با ChatGPT Scheduled
برگشت خروجی تحلیل به Google Drive
انتشار سایت با GitHub Pages
```

## هدف این نسخه

هدف این نسخه ساخت سیستم نهایی نیست؛ هدف این است که مسیر کامل را تست کنیم:

```text
GitHub Extract → Scheduled Analysis → Google Drive Output → GitHub Publish → GitHub Pages
```

## فایل‌های اصلی

```text
.github/workflows/01_extract_test.yml
.github/workflows/02_publish_from_drive.yml
scripts/extract_test.py
scripts/publish_from_drive.py
docs/01_SETUP_GITHUB.md
docs/02_SCHEDULED_TASK_PROMPT.md
docs/03_TEST_SEQUENCE.md
sample_drive_output/pdp_ai_analysis_latest.json
```

## تست سریع

1. محتویات بسته را در ریشه Repository آپلود کن.
2. در GitHub Pages، Source را روی GitHub Actions بگذار.
3. Workflow شماره 01 را اجرا کن.
4. Workflow شماره 02 را با `use_sample=true` اجرا کن.
5. سایت GitHub Pages را ببین.
6. بعد Prompt Scheduled را از `docs/02_SCHEDULED_TASK_PROMPT.md` بساز و تست Drive را انجام بده.
7. Workflow شماره 02 را با `use_sample=false` و Google Doc ID اجرا کن.

## نکته امنیتی

برای نمونه اولیه، خواندن Google Doc با لینک قابل مشاهده انجام می‌شود. در نسخه نهایی بهتر است Google Drive با Service Account یا OAuth امن به GitHub Actions وصل شود.
