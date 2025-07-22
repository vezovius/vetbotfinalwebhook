import telebot
from telebot import types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    markup.row("Erkek", "Dişi")
    bot.send_message(chat_id, "Cinsiyetini seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Erkek", "Dişi"])
def handle_gender(message):
    chat_id = message.chat.id
    user_data[chat_id]["Cinsiyet"] = message.text
    bot.send_message(chat_id, "Yaşını yazınız (örnek: 2 yaşında):")

@bot.message_handler(func=lambda message: "yaş" in message.text or message.text.isdigit())
def handle_age(message):
    chat_id = message.chat.id
    user_data[chat_id]["Yaş"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Evet", "Hayır")
    bot.send_message(chat_id, "Hayvan kısırlaştırıldı mı?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Evet", "Hayır"])
def handle_neuter(message):
    chat_id = message.chat.id
    user_data[chat_id]["Kısır mı"] = message.text
    bot.send_message(chat_id, "Şikayeti nedir?")

@bot.message_handler(func=lambda message: "şikayet" not in user_data.get(message.chat.id, {}))
def handle_complaint(message):
    chat_id = message.chat.id
    user_data[chat_id]["Şikayet"] = message.text
    bot.send_message(chat_id, "Şimdiye kadar kullanılan ilaçları yazınız (varsa):")

@bot.message_handler(func=lambda message: "İlaçlar" not in user_data.get(message.chat.id, {}))
def handle_medications(message):
    chat_id = message.chat.id
    user_data[chat_id]["İlaçlar"] = message.text
    bot.send_message(chat_id, "Teşekkürler. Bilgileriniz kaydedildi.")

bot.infinity_polling()
