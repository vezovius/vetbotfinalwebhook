# -*- coding: utf-8 -*-
"""
VetBot Final (webhook mode for Render)

Conversation flow (Turkish):
1. Hayvan türü (Kedi / Köpek / Kuş / Diğer)
2. Cinsiyet (Erkek / Dişi / Bilmiyorum)
3. Yaş grubu (Yavru / Genç / Yetişkin / Yaşlı)
4. Kısırlaştırma durumu (Kısır / Kısır değil / Bilmiyorum)
5. Şikayet (kullanıcı yazar)
6. Kullanılan ilaçlar (kullanıcı yazar)
Sonunda özet + kayıt (data.json)

Bu dosya polling KULLANMAZ. Yalnızca TELEGRAM WEBHOOK ile çalışır.
Webhook'i mutlaka şu şekilde ayarlayın:
  https://<render-domain>/{BOT_TOKEN}

Gerekli ortam değişkenleri:
  BOT_TOKEN = Telegram bot token

Render yapılandırması (özet):
  requirements.txt -> pyTelegramBotAPI, Flask
  Procfile         -> web: gunicorn main:app
  runtime.txt      -> python-3.10.12  (veya Render desteklediği sürüm)

"""

import os
import json
import logging
from flask import Flask, request, abort

import telebot
from telebot import types

# -------------------------------------------------
# Config
# -------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Parse mode HTML isteğe bağlı
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DATA_FILE = "data.json"

# -------------------------------------------------
# Persistent storage helpers
# -------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logging.exception("data.json okunamadı, sıfırdan başlıyorum")
    return []

def save_data(records):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)

records = load_data()  # list of dict

# Kullanıcı bazlı geçici state
user_state = {}  # chat_id -> {step:int, data:dict}

# -------------------------------------------------
# Reply keyboards
# -------------------------------------------------
def kb(options):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    m.add(*options)
    return m

KB_ANIMAL = kb(["Kedi", "Köpek", "Kuş", "Diğer"])
KB_GENDER = kb(["Erkek", "Dişi", "Bilmiyorum"])
KB_AGE    = kb(["Yavru", "Genç", "Yetişkin", "Yaşlı"])
KB_NEUTER = kb(["Kısır", "Kısır değil", "Bilmiyorum"])

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def start_conversation(chat_id):
    user_state[chat_id] = {"step": 1, "data": {}}
    bot.send_message(chat_id, "Merhaba! Veteriner botuna hoş geldiniz. Hayvan türünü seçin:", reply_markup=KB_ANIMAL)

def cancel_conversation(chat_id):
    user_state.pop(chat_id, None)
    bot.send_message(chat_id, "İşlem iptal edildi. /start ile yeniden başlayabilirsiniz.", reply_markup=types.ReplyKeyboardRemove())

def advance_step(chat_id):
    st = user_state.get(chat_id)
    if not st:
        start_conversation(chat_id)
        return

    step = st["step"]

    if step == 1:
        bot.send_message(chat_id, "Cinsiyetini seçin:", reply_markup=KB_GENDER)
        st["step"] = 2
    elif step == 2:
        bot.send_message(chat_id, "Yaş grubunu seçin:", reply_markup=KB_AGE)
        st["step"] = 3
    elif step == 3:
        bot.send_message(chat_id, "Hayvan kısır mı?", reply_markup=KB_NEUTER)
        st["step"] = 4
    elif step == 4:
        bot.send_message(chat_id, "Lütfen ana şikayeti yazın:", reply_markup=types.ReplyKeyboardRemove())
        st["step"] = 5
    elif step == 5:
        bot.send_message(chat_id, "Şu ana kadar kullanılan ilaçları yazın (yoksa 'yok' yazın):")
        st["step"] = 6
    elif step == 6:
        # Conversation complete
        data = st["data"]
        # Kaydet
        records.append(data)
        save_data(records)
        # Özet
        summary = (
            "Teşekkürler. Alınan bilgiler:\n"
            f"Hayvan türü: {data.get('Hayvan türü','?')}\n"
            f"Cinsiyet: {data.get('Cinsiyet','?')}\n"
            f"Yaş: {data.get('Yaş','?')}\n"
            f"Kısırlaştırma: {data.get('Kısırlaştırma','?')}\n"
            f"Şikayet: {data.get('Şikayet','?')}\n"
            f"İlaçlar: {data.get('İlaçlar','?')}\n"
        )
        bot.send_message(chat_id, summary)
        # Reset
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Yeni bir kayıt için /start yazabilirsiniz.")

# -------------------------------------------------
# Command handlers
# -------------------------------------------------
@bot.message_handler(commands=["start", "başla", "basla"])
def cmd_start(message):
    start_conversation(message.chat.id)

@bot.message_handler(commands=["cancel", "iptal"])
def cmd_cancel(message):
    cancel_conversation(message.chat.id)

# -------------------------------------------------
# Text handler (state machine)
# -------------------------------------------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    txt = message.text.strip()
    st = user_state.get(chat_id)

    if not st:
        bot.send_message(chat_id, "/start ile başlayın lütfen.")
        return

    step = st["step"]
    data = st["data"]

    if step == 1:
        if txt not in ["Kedi","Köpek","Kuş","Diğer"]:
            bot.send_message(chat_id, "Lütfen listedeki seçeneklerden birini seçin.", reply_markup=KB_ANIMAL)
            return
        data['Hayvan türü'] = txt
    elif step == 2:
        if txt not in ["Erkek","Dişi","Bilmiyorum"]:
            bot.send_message(chat_id, "Lütfen listedeki seçeneklerden birini seçin.", reply_markup=KB_GENDER)
            return
        data['Cinsiyet'] = txt
    elif step == 3:
        if txt not in ["Yavru","Genç","Yetişkin","Yaşlı"]:
            bot.send_message(chat_id, "Lütfen listedeki seçeneklerden birini seçin.", reply_markup=KB_AGE)
            return
        data['Yaş'] = txt
    elif step == 4:
        if txt not in ["Kısır","Kısır değil","Bilmiyorum"]:
            bot.send_message(chat_id, "Lütfen listedeki seçeneklerden birini seçin.", reply_markup=KB_NEUTER)
            return
        data['Kısırlaştırma'] = txt
    elif step == 5:
        data['Şikayet'] = txt
    elif step == 6:
        data['İlaçlar'] = txt
    else:
        bot.send_message(chat_id, "/start ile yeni işlem başlatın.")
        return

    advance_step(chat_id)

# -------------------------------------------------
# Flask app & webhook endpoint
# -------------------------------------------------
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'ok', 200

# Telegram webhook bu endpoint'e post eder:
@app.route('/' + BOT_TOKEN, methods=['POST'])
def receive_update():
    try:
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
    except Exception:
        logging.exception("Geçersiz webhook datası")
        abort(400)
    # Telebot'a ilet
    bot.process_new_updates([update])
    return 'OK', 200

# -------------------------------------------------
# Yerel geliştirme için debug çalıştırma
# Render production'da gunicorn Procfile ile başlatır.
# -------------------------------------------------
if __name__ == '__main__':
    # NOT: Lokal testte polling ile hızlı deneme yapmak isterseniz:
    # bot.remove_webhook()
    # bot.infinity_polling()
    # Ancak production'da webhook kullanılacak.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
