import os
import telebot
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

app = Flask(__name__)

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

@app.route('/', methods=["POST"])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/', methods=["GET"])
def index():
    return "VetBot is running!", 200