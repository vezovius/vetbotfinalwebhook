from flask import Flask, request
import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN', '7776065669:AAEWGA0PI1Hs0NwuNTRQUGU8Atkeuhbetdg')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_URL') + TOKEN)
    return 'Webhook set!', 200

# مثال ساده پیام
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Hayvan türünü giriniz:")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Teşekkürler!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
