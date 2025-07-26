
import telebot
import json
from datetime import datetime

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 67178220

# Load data from JSON file or initialize it
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save data to JSON file
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()

# Step keys in Turkish
steps = ["Tür", "Cinsiyet", "Yaş", "Kısırlaştırılmış mı?", "Şikayet", "Kullanılan ilaçlar"]

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": 0, "answers": []}
    bot.send_message(chat_id, "Veteriner hasta kayıt botuna hoş geldiniz!")
    ask_question(chat_id)

def ask_question(chat_id):
    step = user_data[chat_id]["step"]
    if step == 0:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Kedi", "Köpek", "Kuş")
        bot.send_message(chat_id, "1️⃣ Hayvan türü nedir?", reply_markup=markup)
    elif step == 1:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Erkek", "Dişi")
        bot.send_message(chat_id, "2️⃣ Cinsiyeti nedir?", reply_markup=markup)
    elif step == 2:
        bot.send_message(chat_id, "3️⃣ Yaşını giriniz (örn. 2 yaşında):")
    elif step == 3:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Evet", "Hayır")
        bot.send_message(chat_id, "4️⃣ Kısırlaştırılmış mı?", reply_markup=markup)
    elif step == 4:
        bot.send_message(chat_id, "5️⃣ Ana şikayeti yazınız:")
    elif step == 5:
        bot.send_message(chat_id, "6️⃣ Kullanılan ilaçları yazınız:")
    else:
        finalize(chat_id)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {"step": 0, "answers": []}

    step = user_data[chat_id]["step"]
    user_data[chat_id]["answers"].append(message.text)
    user_data[chat_id]["step"] += 1

    if user_data[chat_id]["step"] < len(steps):
        ask_question(chat_id)
    else:
        finalize(chat_id)

def finalize(chat_id):
    answers = user_data[chat_id]["answers"]
    text = "
".join([f"{i+1}. {steps[i]}: {answers[i]}" for i in range(len(steps))])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_text = f"📝 Yeni Hasta Kaydı ({timestamp}):

{text}"
    bot.send_message(chat_id, "Teşekkürler! Bilgileriniz kaydedildi.")
    bot.send_message(ADMIN_ID, final_text)
    save_data(user_data)
    user_data.pop(chat_id)

# Command to send data.json to admin
@bot.message_handler(commands=["veri"])
def send_data_file(message):
    if message.from_user.id == ADMIN_ID:
        try:
            with open("data.json", "rb") as f:
                bot.send_document(message.chat.id, f)
        except Exception as e:
            bot.send_message(message.chat.id, "Dosya gönderilemedi.")

bot.infinity_polling()
