import os
import telebot
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_data = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Kedi", "Köpek", "Kuş")
    bot.send_message(chat_id, "Hayvan türünü seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Kedi", "Köpek", "Kuş"])
def handle_animal_type(message):
    chat_id = message.chat.id
    user_data[chat_id]["Tür"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Erkek", "Dişi")
    bot.send_message(chat_id, "Cinsiyetini seçiniz:", reply_markup=markup)

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    return "!", 403

if __name__ == "__main__":
    import logging
    import sys

    webhook_url = "https://vetbotfinalwebhook.onrender.com"  # Replace if needed
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)