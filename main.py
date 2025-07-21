
from flask import Flask, request
import telebot
import json

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# تاریخچه بیماران ذخیره می‌شود
def save_data(chat_id, key, value):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    if str(chat_id) not in data:
        data[str(chat_id)] = {}
    data[str(chat_id)][key] = value

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# خوش‌آمدگویی با صدا و شروع دکمه‌ها
@bot.message_handler(commands=["start"])
def welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Veteriner Bilgi Botuna Hoş Geldiniz 🐾")
    with open("hosgeldin.mp3", "rb") as voice:
        bot.send_voice(chat_id, voice)
    animal_type_buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    animal_type_buttons.add("Kedi", "Köpek", "Kuş")
    bot.send_message(chat_id, "Lütfen hayvanın türünü seçin:", reply_markup=animal_type_buttons)

@bot.message_handler(func=lambda m: m.text in ["Kedi", "Köpek", "Kuş"])
def get_gender(message):
    save_data(message.chat.id, "Tür", message.text)
    gender_buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    gender_buttons.add("Dişi", "Erkek")
    bot.send_message(message.chat.id, "Cinsiyeti seçin:", reply_markup=gender_buttons)

@bot.message_handler(func=lambda m: m.text in ["Dişi", "Erkek"])
def get_age(message):
    save_data(message.chat.id, "Cinsiyet", message.text)
    bot.send_message(message.chat.id, "Yaşını giriniz:")
    bot.register_next_step_handler(message, get_neuter)

def get_neuter(message):
    save_data(message.chat.id, "Yaş", message.text)
    neuter_buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    neuter_buttons.add("Kısır", "Kısır değil")
    bot.send_message(message.chat.id, "Kısırlaştırma durumu:", reply_markup=neuter_buttons)

@bot.message_handler(func=lambda m: m.text in ["Kısır", "Kısır değil"])
def get_complaint(message):
    save_data(message.chat.id, "Kısırlaştırma", message.text)
    bot.send_message(message.chat.id, "Ana şikayeti yazınız:")
    bot.register_next_step_handler(message, get_medications)

def get_medications(message):
    save_data(message.chat.id, "Şikayet", message.text)
    bot.send_message(message.chat.id, "Kullanılan ilaçları yazınız:")
    bot.register_next_step_handler(message, finish)

def finish(message):
    save_data(message.chat.id, "İlaçlar", message.text)
    bot.send_message(message.chat.id, "Bilgiler kaydedildi. Teşekkürler!")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://neovetbot.onrender.com/YOUR_BOT_TOKEN")
    app.run(host="0.0.0.0", port=10000)
