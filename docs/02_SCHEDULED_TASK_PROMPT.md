# پرامپت Scheduled برای تست مسیر GitHub → ChatGPT Scheduled → Google Drive

بعد از اینکه Workflow شماره 01 را اجرا کردی، فایل زیر در GitHub ساخته می‌شود:

```text
https://raw.githubusercontent.com/<OWNER>/<REPO>/main/outputs/pdp_normalized_latest.json
```

یک Google Doc بساز یا از فایل تست موفق استفاده کن و آن را خروجی تحلیل قرار بده. سپس Scheduled Task را با متن زیر بساز یا دستی اجرا کن.

---

## Prompt Template

```text
تو تحلیلگر مناقصات و استعلامات شرکت مهندسین مشاور طرح و برنامه پارس PDP هستی.

هدف:
فایل نرمال‌شده مناقصات و استعلامات را از GitHub بخوان، موارد مناسب PDP را تحلیل کن، و خروجی نهایی را به صورت JSON معتبر داخل Google Doc خروجی جایگزین کن.

ورودی GitHub:
https://raw.githubusercontent.com/<OWNER>/<REPO>/main/outputs/pdp_normalized_latest.json

Google Doc خروجی برای نوشتن JSON:
https://docs.google.com/document/d/<GOOGLE_DOC_ID>/edit

قواعد انتخاب:
- موارد مرتبط با خدمات مهندسین مشاور، طراحی، مطالعات، ماده 23، امکان‌سنجی، شهرسازی، ساختمان، سازه، تأسیسات، انرژی، GIS، نظارت، مدیریت طرح و مناطق ویژه را پیشنهاد بده.
- موارد خرید صرف کالا، تأمین تجهیزات، تنظیف، نیروی انسانی، تعمیرات ساده و اجرای صرف بدون مشاوره/طراحی/نظارت را رد کن.
- مناقصات و استعلامات را جدا کن.
- برای هر پیشنهاد اهمیت، فوریت، امتیاز، دلیل انتخاب، اقدام پیشنهادی، ریسک و میزان اطمینان بده.
- خروجی فقط JSON معتبر باشد. متن اضافه، Markdown و code fence ننویس.

قالب خروجی:
{
  "schema_version": "pdp-scheduled-analysis-v1",
  "generated_at": "...",
  "analysis_method": "ChatGPT Scheduled Task",
  "source": {
    "github_owner": "<OWNER>",
    "github_repo": "<REPO>",
    "file": "outputs/pdp_normalized_latest.json"
  },
  "suggested_tenders": [],
  "suggested_inquiries": [],
  "rejected_items": [],
  "dashboard": {
    "total_input_items": 0,
    "suggested_tenders_count": 0,
    "suggested_inquiries_count": 0,
    "urgent_count": 0,
    "by_category": {},
    "by_source": {}
  },
  "notes": []
}

اگر فایل GitHub خوانده نشد یا نوشتن در Google Drive ممکن نبود، داخل همان Google Doc یک JSON با status="failed" و توضیح خطا بنویس.
```

---

## نکته مهم

برای تست، ابتدا همین Prompt را دستی اجرا کن. وقتی مطمئن شدی Google Doc بدون درخواست Allow اضافی به‌روزرسانی می‌شود، آن را Scheduled روزانه کن.
