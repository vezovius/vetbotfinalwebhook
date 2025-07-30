import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN", "توکن_اینجا_بگذار")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# دستور شروع
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Merhaba! Hayvan türünü giriniz.")

# دریافت متن
@bot.message_handler(func=lambda message: True)
def save_message(message):
    bot.reply_to(message, f"Teşekkürler! '{message.text}' kaydedildi.")

# مسیر وبهوک
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# مسیر اصلی برای تست
@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    # ست کردن وبهوک به صورت خودکار
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
