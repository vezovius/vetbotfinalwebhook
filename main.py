
import os
import telebot
from telebot import types
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()  # حذف webhook قبل از استفاده از polling


bot = telebot.TeleBot(BOT_TOKEN)

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
    markup.row("Dişi", "Erkek")
    bot.send_message(chat_id, "Cinsiyetini seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Dişi", "Erkek"])
def handle_gender(message):
    chat_id = message.chat.id
    user_data[chat_id]["Cinsiyet"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Yavru", "Genç", "Yetişkin")
    bot.send_message(chat_id, "Yaşını seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Yavru", "Genç", "Yetişkin"])
def handle_age(message):
    chat_id = message.chat.id
    user_data[chat_id]["Yaş"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Kısır", "Kısır değil")
    bot.send_message(chat_id, "Kısırlaştırılmış mı?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Kısır", "Kısır değil"])
def handle_neuter(message):
    chat_id = message.chat.id
    user_data[chat_id]["Kısırlaştırma"] = message.text
    bot.send_message(chat_id, "Ana şikayeti yazınız:")

@bot.message_handler(func=lambda message: "Kısırlaştırma" in user_data.get(message.chat.id, {}))
def handle_complaint(message):
    chat_id = message.chat.id
    user_data[chat_id]["Şikayet"] = message.text
    bot.send_message(chat_id, "Kullanılan ilaçları yazınız:")

@bot.message_handler(func=lambda message: "Şikayet" in user_data.get(message.chat.id, {}))
def handle_medications(message):
    chat_id = message.chat.id
    user_data[chat_id]["İlaçlar"] = message.text

    # Save to JSON
    with open("data.json", "a", encoding="utf-8") as f:
        json.dump({chat_id: user_data[chat_id]}, f, ensure_ascii=False)
        f.write("\n")

    summary = "\n".join([f"{k}: {v}" for k, v in user_data[chat_id].items()])
    bot.send_message(chat_id, f"Teşekkürler. Alınan bilgiler:\n{summary}")

bot.polling()
