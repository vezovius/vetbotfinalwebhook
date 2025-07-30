import os
import json
from flask import Flask, request, abort
import telebot
from telebot import types

# --- Config -----------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set.")

# Storage file (JSON) - relative to working dir
DATA_FILE = "data.json"

# Choices (Turkish)
ANIMALS = ["Kedi", "Köpek", "Kuş"]
SEXES = ["Erkek", "Dişi"]
AGES = ["Yavru", "Genç", "Yetişkin", "Yaşlı"]
NEUTER = ["Kısır", "Kısır Değil", "Bilmiyorum"]

# -----------------------------------------------------------------------------
# Helpers for simple JSON persistence
def _load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("WARN: could not save data:", e, flush=True)

user_data = _load_data()

# -----------------------------------------------------------------------------
# TeleBot (threaded=False because Flask will drive updates)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False, parse_mode=None)

app = Flask(__name__)

# -----------------------------------------------------------------------------
# Conversation flow
#
# We'll gate each step by checking which key is missing in user_data[chat_id].
# Keys: Tur (animal), Cinsiyet, Yas, Kisir, Sikayet, Ilaclar
#

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # reset conversation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for label in ANIMALS:
        markup.add(label)
    bot.send_message(chat_id, "Hayvan türünü seçiniz:", reply_markup=markup)
    _save_data(user_data)

# --- animal type -------------------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Tur" not in user_data[m.chat.id] and m.text in ANIMALS)
def handle_animal_type(message):
    chat_id = message.chat.id
    user_data[chat_id]["Tur"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for label in SEXES:
        markup.add(label)
    bot.send_message(chat_id, "Cinsiyetini seçiniz:", reply_markup=markup)
    _save_data(user_data)

# --- sex ---------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Tur" in user_data[m.chat.id] and "Cinsiyet" not in user_data[m.chat.id] and m.text in SEXES)
def handle_sex(message):
    chat_id = message.chat.id
    user_data[chat_id]["Cinsiyet"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for label in AGES:
        markup.add(label)
    bot.send_message(chat_id, "Yaş grubunu seçiniz:", reply_markup=markup)
    _save_data(user_data)

# --- age ---------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Cinsiyet" in user_data[m.chat.id] and "Yas" not in user_data[m.chat.id] and m.text in AGES)
def handle_age(message):
    chat_id = message.chat.id
    user_data[chat_id]["Yas"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for label in NEUTER:
        markup.add(label)
    bot.send_message(chat_id, "Hayvan kısır mı?", reply_markup=markup)
    _save_data(user_data)

# --- neuter ------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Yas" in user_data[m.chat.id] and "Kisir" not in user_data[m.chat.id] and m.text in NEUTER)
def handle_neuter(message):
    chat_id = message.chat.id
    user_data[chat_id]["Kisir"] = message.text
    # free text step (complaint)
    hide = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Ana şikayet nedir? (lütfen yazınız)", reply_markup=hide)
    _save_data(user_data)

# --- complaint (free text) ---------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Kisir" in user_data[m.chat.id] and "Sikayet" not in user_data[m.chat.id])
def handle_complaint(message):
    chat_id = message.chat.id
    user_data[chat_id]["Sikayet"] = message.text
    bot.send_message(chat_id, "Şimdiye kadar kullanılan ilaç(lar)? (lütfen yazınız)")
    _save_data(user_data)

# --- meds (free text) --------------------------------------------------------
@bot.message_handler(func=lambda m: m.chat.id in user_data and "Sikayet" in user_data[m.chat.id] and "Ilaclar" not in user_data[m.chat.id])
def handle_meds(message):
    chat_id = message.chat.id
    user_data[chat_id]["Ilaclar"] = message.text

    # summary
    lines = [f"{k}: {v}" for k, v in user_data[chat_id].items()]
    summary = "\n".join(lines)
    bot.send_message(chat_id, f"Teşekkürler. Alınan bilgiler:\n{summary}")

    # persist
    _save_data(user_data)

    # optionally clear conversation comment out if want repeated
    # del user_data[chat_id]

# -----------------------------------------------------------------------------
# Flask routes
#

@app.route("/", methods=["GET"])
def index():
    return "vetbotfinalwebhook up", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "ok", 200
    abort(403)

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # For local test: you can set webhook manually:
    # import requests
    # requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=http://<public-url>/{BOT_TOKEN}")
    print(f"Starting Flask server on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port)
