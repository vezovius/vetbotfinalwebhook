import os
import logging
from flask import Flask, request
import telegram

TOKEN = os.environ.get("TOKEN", "7776065669:AAEWGA0P1IHsONwuNTRQUGU8Atekuhbetdg")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# Webhook endpoint
@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    text = update.message.text

    bot.send_message(chat_id=chat_id, text="Merhaba! Veteriner Botuna hoş geldiniz 🐾")
    bot.send_message(chat_id=chat_id, text=f"Gönderdiğiniz mesaj: {text}")

    return "ok"

# Health check endpoint
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
