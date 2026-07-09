# راه‌اندازی نمونه اولیه در GitHub

## 1) آپلود فایل‌ها

محتوای این بسته را در ریشه Repository قرار بده؛ نه داخل یک پوشه اضافه.

در ریشه Repository باید این‌ها را ببینی:

```text
.github/workflows/01_extract_test.yml
.github/workflows/02_publish_from_drive.yml
scripts/extract_test.py
scripts/publish_from_drive.py
sample_drive_output/pdp_ai_analysis_latest.json
```

## 2) فعال کردن GitHub Pages

در Repository برو به:

```text
Settings → Pages
```

در بخش Source، حالت GitHub Actions را انتخاب کن.

## 3) اجرای تست Extract

برو به:

```text
Actions → 01 - PDP Extract Test → Run workflow
```

بعد از پایان اجرا باید این فایل‌ها در Repository ساخته شوند:

```text
outputs/pdp_normalized_latest.json
outputs/pdp_summary_latest.json
```

## 4) اجرای تست Publish با نمونه داخلی

برای اینکه اول فقط GitHub Pages را تست کنیم:

```text
Actions → 02 - PDP Publish From Drive → Run workflow
```

ورودی‌ها:

```text
use_sample = true
analysis_doc_id = خالی
```

اگر موفق شد، سایت GitHub Pages بالا می‌آید.

## 5) اجرای Publish از Google Drive

بعد از اینکه Scheduled خروجی JSON را در Google Doc نوشت:

```text
Actions → 02 - PDP Publish From Drive → Run workflow
```

ورودی‌ها:

```text
use_sample = false
analysis_doc_id = شناسه Google Doc خروجی
```

شناسه Google Doc همان بخش وسط لینک است:

```text
https://docs.google.com/document/d/<THIS_IS_DOC_ID>/edit
```

برای نمونه اولیه، Google Doc باید قابل خواندن با لینک باشد؛ یعنی Share روی Anyone with the link can view قرار بگیرد. در نسخه نهایی می‌توانیم روش امن‌تر با Service Account بگذاریم.
