# Vet Bot (Webhook Version)

این نسخه از بات تلگرام مخصوص اجرا روی Render است و از **Webhook** استفاده می‌کند (نه polling).  
لطفاً دستورالعمل زیر را برای استقرار دنبال کنید.

## متغیرهای محیطی لازم
- `BOT_TOKEN` — توکن ربات از BotFather
- `WEBHOOK_URL` — آدرس کامل HTTPS سرویس شما در Render + `/webhook`
  مثال: `https://vetbotfinalwebhook.onrender.com/webhook`

## فرمان‌های Render
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn main:app --bind 0.0.0.0:$PORT`
  (Render متغیر PORT را تزریق می‌کند)

## نکات
- در این نسخه هیچ `bot.polling()` وجود ندارد؛ پس خطای 409 Conflict نمی‌گیرید.
- اگر قبلاً همان Bot Token در جای دیگری (مثلاً Replit) polling می‌شده است، آن سرویس را متوقف کنید.
- داده‌های دریافت‌شده در فایل `data.json` ذخیره می‌شوند.

## اجرای لوکال
```bash
export BOT_TOKEN=xxx
export WEBHOOK_URL=http://<ngrok-url>/webhook   # فقط برای تست
python main.py
```
سپس ngrok یا سرویس مشابه استفاده کنید تا تلگرام بتواند پست کند.
