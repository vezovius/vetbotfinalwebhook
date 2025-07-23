# VetBot Final Webhook

Telegram veterinary intake bot (Turkish) running in *webhook* mode (no polling) for free Render or other PaaS.

## Quick Env Vars

- BOT_TOKEN – your bot token from @BotFather.
- WEBHOOK_BASE_URL – (optional) public base URL of your deployed app, e.g. https://vetbotfinalwebhook.onrender.com
  If set, the app will auto-call setWebhook() on startup pointing to <BASE>/<BOT_TOKEN>.

If you do **not** set WEBHOOK_BASE_URL, deploy first, then manually set the webhook:

https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-app.onrender.com/<YOUR_TOKEN>

Replace <YOUR_TOKEN> and hostname appropriately.

## Health Check

GET / returns 200 text "VetBot webhook is running." – use this for UptimeRobot/BetterStack monitors.

## Conversation Flow
Animal → Sex → Age → Neutered → Complaint (free text) → Medications (free text) → Summary.

Responses saved (append) to data.json in working dir (ephemeral on free tiers).

Generated for you. ❤️
