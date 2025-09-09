Telegram WooCommerce Price Bot
================================

ربات ساده تلگرام برای به‌روزرسانی قیمت محصولات ووکامرس با ارسال فایل اکسل.

امکانات
-------
- دریافت فایل اکسل `.xlsx` از تلگرام
- پردازش ستون‌های `كد كالا`, `قيمت فروش  ` و اختیاری `مبلغ تخفيف`
- محاسبه `regular_price` و `sale_price`
- به‌روزرسانی دسته‌ای محصولات از طریق WooCommerce REST API

راه‌اندازی
---------
1) نصب وابستگی‌ها:
```
pip install -r requirements.txt
```

2) تنظیم متغیرها:
یک فایل `.env` در ریشه بسازید:
```
BOT_TOKEN=your_telegram_bot_token
WOOCOMMERCE_CONSUMER_KEY=ck_xxx
WOOCOMMERCE_CONSUMER_SECRET=cs_xxx
WOOCOMMERCE_BASE_URL=https://example.com/wp-json/wc/v3
ADMIN_IDS=123456789
BATCH_SIZE=20
REQUEST_DELAY=0.2
LOG_LEVEL=INFO
```

3) اجرای ربات:
```
python -m bot.main
```

فرمت اکسل
---------
- `كد كالا`: اجباری (SKU)
- `قيمت فروش  `: اجباری (توجه به دو فاصله انتهایی)
- `مبلغ تخفيف`: اختیاری

نکات امنیتی
----------
- کلیدها را در `.env` نگه دارید، هرگز در کد قرار ندهید.
- اگر SSL معتبر دارید، گزینه `verify` را در درخواست‌ها فعال نگه دارید.

استقرار (اختیاری)
---------------
- می‌توانید با GitHub Actions و Railway/Render مستقر کنید.
- دستور اجرای سرویس: `python -m bot.main`

### Railway
- فایل‌های `railway.json` و `Procfile` اضافه شده‌اند.
- در GitHub → Settings → Secrets مقدار `RAILWAY_TOKEN` را اضافه کنید.
- هر push به `main` به‌صورت خودکار دیپلوی می‌شود (`.github/workflows/railway-deploy.yml`).


