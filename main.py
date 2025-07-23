import os
import json
from flask import Flask, request
import telebot
from telebot import types

# --- ENV ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var missing!")

# --- TeleBot ---
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# داده‌های موقت کاربر (حافظه RAM؛ برای ذخیره‌ دائمی بعداً json file یا DB اضافه می‌کنیم)
user_data = {}

# --- فلَسک ---
app = Flask(__name__)

# سلامت برای UptimeRobot
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

# وبهوک تلگرام: تلگرام POST می‌فرستد به /<توکن>
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update_json = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json.loads(update_json))
        bot.process_new_updates([update])
    except Exception as e:
        # لاگ ساده به استریم استاندارد (در Render در لاگ‌ها می‌بینی)
        print(f"[webhook] error: {e}", flush=True)
    return "", 200


# --- بات هندلرها ---

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Kedi", "Köpek", "Kuş")
    bot.send_message(chat_id, "Hayvan türünü seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "Tür" not in user_data[m.chat.id] and m.text in ["Kedi", "Köpek", "Kuş"])
def handle_animal_type(message):
    chat_id = message.chat.id
    user_data[chat_id]["Tür"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Erkek", "Dişi")
    bot.send_message(chat_id, "Cinsiyet seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "Cinsiyet" not in user_data[m.chat.id] and m.text in ["Erkek", "Dişi"])
def handle_gender(message):
    chat_id = message.chat.id
    user_data[chat_id]["Cinsiyet"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Yavru", "Genç", "Yetişkin", "Yaşlı")
    bot.send_message(chat_id, "Yaş grubunu seçiniz:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "Yaş" not in user_data[m.chat.id] and m.text in ["Yavru", "Genç", "Yetişkin", "Yaşlı"])
def handle_age(message):
    chat_id = message.chat.id
    user_data[chat_id]["Yaş"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("Kısır", "Kısır değil")
    bot.send_message(chat_id, "Hayvan kısır mı?", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "Kısır" not in user_data[m.chat.id] and m.text in ["Kısır", "Kısır değil"])
def handle_neuter(message):
    chat_id = message.chat.id
    user_data[chat_id]["Kısır"] = message.text
    bot.send_message(chat_id, "Ana şikayet nedir? (lütfen yazınız)")
    
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Şikayet" not in user_data[m.chat.id])
def handle_complaint(message):
    chat_id = message.chat.id
    user_data[chat_id]["Şikayet"] = message.text
    bot.send_message(chat_id, "Şimdiye kadar kullanılan ilaç(lar)? (lütfen yazınız)")
    
@bot.message_handler(func=lambda m: m.chat.id in user_data and "İlaçlar" not in user_data[m.chat.id])
def handle_meds(message):
    chat_id = message.chat.id
    user_data[chat_id]["İlaçlar"] = message.text
    
    # خلاصه
    summary_lines = [f"{k}: {v}" for k, v in user_data[chat_id].items()]
    summary = "\n".join(summary_lines)
    bot.send_message(chat_id, f"Teşekkürler. Alınan bilgiler:\n{summary}")
    # TODO: ذخیره در فایل json یا DB
    
    # بعد از اتمام، اگر می‌خواهی داده ریست شود:
    # del user_data[chat_id]


# --- اجرای سرویس ---
def main():
    # در این نسخه *وبهوک را در کد ست نمی‌کنیم* چون دستی ست کردی.
    # اگر خواستی خودکار شود، این دو خط را آزاد کن (و حتماً URL درست بده):
    # bot.remove_webhook()
    # bot.set_webhook(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'vetbotfinalwebhook.onrender.com')}/{BOT_TOKEN}")
    #
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()