
import telebot
import os
import json

TOKEN = "YOUR_BOT_TOKEN"  # توکن ربات
ADMIN_ID = 67178220  # شناسه عددی تلگرام شما

bot = telebot.TeleBot(TOKEN)

# ذخیره داده‌ها
def save_user_data(user_id, data):
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
    else:
        all_data = {}

    all_data[str(user_id)] = data

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

# شروع گفتگو
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Merhaba! Hayvan türünü giriniz:")

# گرفتن داده از کاربر
@bot.message_handler(func=lambda m: True)
def collect_data(message):
    user_id = message.from_user.id
    data = {"cevap": message.text}
    save_user_data(user_id, data)
    bot.reply_to(message, "Teşekkürler!")

# ارسال فایل دیتا.json به ادمین
@bot.message_handler(commands=["veri"])
def send_data_file(message):
    if message.from_user.id == ADMIN_ID:
        if os.path.exists("data.json"):
            with open("data.json", "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "Kayıtlı veri bulunamadı.")
    else:
        bot.reply_to(message, "Bu komut yalnızca yöneticiye özeldir.")

print("Bot çalışıyor...")
bot.polling()
