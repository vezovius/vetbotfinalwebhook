# VetBot Final Webhook

Bu repo Render üzerinde 7/24 çalışabilen basit bir Telegram veteriner botu içindir.

## Hızlı Başlangıç

1. **BOT_TOKEN** değerini Render > Environment'da ekleyin.
2. Deploy edin.
3. Webhook ayarlayın:

```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<render-domain>/<YOUR_TOKEN>
```

Örnek:
```
https://api.telegram.org/bot123456:ABC/setWebhook?url=https://vetbotfinalwebhook.onrender.com/123456:ABC
```

4. Telegram'da `/start` yazın.

Detaylar için main.py içindeki yorumlara bakın.
