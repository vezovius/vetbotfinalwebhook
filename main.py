from flask import Flask, request
import telebot
import json
import os

TOKEN = os.getenv("BOT_TOKEN", "7776065669:AAEWGA0PI1Hs0NwuNTRQUGU8Atkeuhbetdg")
ADMIN_ID = int(os.getenv("ADMIN_ID", "67178220"))
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)

# لود دیتا
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

questions = [
    ("animal", "Hayvan türünü giriniz:"),
    ("gender", "Cinsiyetini giriniz:"),
    ("age", "Yaşını giriniz:"),
    ("neutered", "Kısır mı? (Evet/Hayır)"),
    ("complaint", "Ana şikayetini yazınız:"),
    ("medications", "Şu ana kadar kullanılan ilaçları yazınız:")
]

user_states = {}

@bot.message_handler(commands=["start"])
def start(message):
    user_states[message.chat.id] = 0
    bot.send_message(message.chat.id, questions[0][1])

@bot.message_handler(commands=["veri"])
def send_data(message):
    if message.from_user.id == ADMIN_ID:
        if os.path.exists(DATA_FILE):
            bot.send_document(message.chat.id, open(DATA_FILE, "rb"))
        else:
            bot.send_message(message.chat.id, "Henüz veri yok.")
    else:
        bot.send_message(message.chat.id, "Bu komut yalnızca admin içindir.")

@bot.message_handler(func=lambda m: True)
def form_handler(message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        bot.send_message(chat_id, "Lütfen /start komutu ile başlayınız.")
        return

    step = user_states[chat_id]
    key, _ = questions[step]
    user_data.setdefault(str(chat_id), {})[key] = message.text

    if step + 1 < len(questions):
        user_states[chat_id] += 1
        bot.send_message(chat_id, questions[step + 1][1])
    else:
        bot.send_message(chat_id, "Teşekkürler! Formunuz tamamlandı.")
        user_states.pop(chat_id)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

bot.polling()
