# Vet Bot Final (Webhook Only)

Basit bir veteriner triage Telegram botu. Flask + pyTelegramBotAPI.
Bu sürüm **webhook** modunda çalışır (polling yok). Render Free plan ile uyumlu.

## Çalıştırma (Lokal test için)
1. `export BOT_TOKEN=...`
2. `pip install -r requirements.txt`
3. `python main.py`
4. ngrok gibi bir araçla portu yayınlayın ve Telegram webhook ayarlayın:
   ```
   curl "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=https://<ngrok-url>/$BOT_TOKEN"
   ```

## Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Env Var: `BOT_TOKEN` (zorunlu)
- Deploy et. Live olunca:
  ```
  https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<render-app>/$BOT_TOKEN
  ```
- `/start` yazın ve adımları takip edin.

Veriler `data.json` dosyasında saklanır.
