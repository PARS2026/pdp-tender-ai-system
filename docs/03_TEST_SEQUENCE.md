# ترتیب تست کامل نمونه اولیه

## هدف تست

می‌خواهیم ثابت کنیم این زنجیره کار می‌کند:

```text
GitHub Extract → GitHub normalized JSON → ChatGPT Scheduled → Google Drive JSON → GitHub Publish → GitHub Pages
```

## ترتیب پیشنهادی

### مرحله 1: اجرای Extract

در GitHub Actions، workflow زیر را اجرا کن:

```text
01 - PDP Extract Test
```

خروجی مورد انتظار:

```text
outputs/pdp_normalized_latest.json
```

### مرحله 2: آماده کردن Prompt Scheduled

در فایل زیر Prompt آماده است:

```text
docs/02_SCHEDULED_TASK_PROMPT.md
```

در Prompt این موارد را جایگزین کن:

```text
<OWNER>
<REPO>
<GOOGLE_DOC_ID>
```

### مرحله 3: اجرای Scheduled یا دستی ChatGPT

Prompt را اجرا کن تا خروجی تحلیل‌شده داخل Google Doc نوشته شود.

خروجی Google Doc باید فقط JSON معتبر باشد.

### مرحله 4: اجرای Publish

در GitHub Actions، workflow زیر را اجرا کن:

```text
02 - PDP Publish From Drive
```

ورودی‌ها:

```text
use_sample = false
analysis_doc_id = GOOGLE_DOC_ID
```

### مرحله 5: بررسی سایت

بعد از پایان Workflow، لینک GitHub Pages را باز کن و این صفحات را چک کن:

```text
داشبورد
مناقصات پیشنهادی
استعلامات پیشنهادی
ردشده‌ها
دانلود JSON
```

## اگر Publish خطا داد

احتمال‌های رایج:

1. Google Doc هنوز JSON معتبر ندارد.
2. Google Doc قابل خواندن با لینک نیست.
3. Doc ID اشتباه وارد شده.
4. خروجی Scheduled داخل code fence نوشته شده؛ اسکریپت تا حدی این را حذف می‌کند، ولی بهتر است خروجی فقط JSON خام باشد.
