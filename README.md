# VetBot Webhook Package

Minimal Telegram veterinary intake bot (Turkish) designed for Render free Web Service (webhook mode).

## Files
* `main.py` – Flask + TeleBot webhook app.
* `requirements.txt` – Python deps.
* `runtime.txt` – Optional Python version hint.
* `data.json` – Stored user submissions (created at runtime if missing).

## Deploy (Render)
1. Create new **Web Service** from this repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `python main.py`
4. Add environment variable **BOT_TOKEN** with your Telegram bot token.
5. After first deploy, set Telegram webhook:

   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-render-service-name>.onrender.com/bot<YOUR_TOKEN>
   ```

6. Ping `https://<your-render-service-name>.onrender.com/` periodically (UptimeRobot) to reduce spin-up latency.

## Conversation Flow
`/start` -> Hayvan türü -> Cinsiyet -> Yaş grubu -> Kısırlaştırılmış mı -> Ana şikayet -> Kullanılan ilaçlar -> Özet + kayıt.
