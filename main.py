import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# شروع مکالمه
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Hayvan türünü giriniz:")

# پاسخ به پیام
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, f"Teşekkürler! {message.text} kaydedildi.")

# Webhook route
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    return "Bot is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
