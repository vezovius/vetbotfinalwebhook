import os
import json
import logging
from typing import Dict, Any

from flask import Flask, request
import telebot
from telebot import types

# ------------------------------------------------------------------
# Configuration (from environment)
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g. https://vetbotfinalwebhook.onrender.com/webhook

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)  # plain text

# ------------------------------------------------------------------
# State store (in-memory) + simple JSON persistence
# ------------------------------------------------------------------
user_state: Dict[int, str] = {}     # chat_id -> current step
user_data: Dict[int, Dict[str, Any]] = {}  # chat_id -> collected fields

DATA_FILE = "data.json"


def load_data() -> None:
    """Load previously saved user data from disk (best-effort)."""
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # keys saved as strings -> convert to int
                user_data = {int(k): v for k, v in raw.items()}
        except Exception as e:
            logging.warning("Couldn't load data.json: %s", e)


def save_data() -> None:
    """Persist user_data to disk (best-effort)."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in user_data.items()}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error("Couldn't save data.json: %s", e)


load_data()

# ------------------------------------------------------------------
# Conversation texts (Turkish)
# ------------------------------------------------------------------
TXT_WELCOME = "Merhaba! Veteriner botuna hoş geldiniz. Lütfen hayvan türünü seçin:"
TXT_CHOOSE_ANIMAL = "Hayvan türünü seçiniz:"
TXT_CHOOSE_GENDER = "Cinsiyetini seçiniz:"
TXT_ENTER_AGE = "Yaşını yazınız (örn: 2 yaş, 8 ay):"
TXT_CHOOSE_NEUTER = "Hayvan kısırlaştırılmış mı?"
TXT_ENTER_COMPLAINT = "Ana şikayet nedir? Lütfen kısaca yazınız."
TXT_ENTER_MEDS = "Şimdiye kadar verilen ilaçları yazınız (yoksa 'yok' yazın)."
TXT_THANKS = "Teşekkürler. Alınan bilgiler:"
TXT_CANCELLED = "İşlem iptal edildi. /start ile yeniden başlayabilirsiniz."

BTN_CAT = "Kedi"
BTN_DOG = "Köpek"
BTN_BIRD = "Kuş"

BTN_MALE = "Erkek"
BTN_FEMALE = "Dişi"

BTN_NEUTERED = "Kısırlaştırılmış"
BTN_INTACT = "Kısırlaştırılmamış"

BTN_CANCEL = "İptal"


# ------------------------------------------------------------------
# Keyboards
# ------------------------------------------------------------------
def keyboard_animals():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(BTN_CAT, BTN_DOG, BTN_BIRD)
    kb.row(BTN_CANCEL)
    return kb


def keyboard_gender():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(BTN_MALE, BTN_FEMALE)
    kb.row(BTN_CANCEL)
    return kb


def keyboard_neuter():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(BTN_NEUTERED, BTN_INTACT)
    kb.row(BTN_CANCEL)
    return kb


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------
def start_conversation(chat_id: int) -> None:
    user_state[chat_id] = "animal"
    user_data[chat_id] = {}
    bot.send_message(chat_id, TXT_WELCOME, reply_markup=keyboard_animals())


def reset_conversation(chat_id: int) -> None:
    if chat_id in user_state:
        del user_state[chat_id]
    if chat_id in user_data:
        del user_data[chat_id]


def finalize_conversation(chat_id: int) -> None:
    """Send summary + persist to disk."""
    data = user_data.get(chat_id, {})
    lines = []
    if data:
        for k, v in data.items():
            lines.append(f"- {k}: {v}")
    summary = "\n".join(lines) if lines else "(veri yok)"
    bot.send_message(chat_id, f"{TXT_THANKS}\n{summary}")
    save_data()
    # reset state so new /start later begins fresh
    reset_conversation(chat_id)


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    start_conversation(message.chat.id)


@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    reset_conversation(message.chat.id)
    bot.send_message(message.chat.id, TXT_CANCELLED, reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # If no state, require /start
    if chat_id not in user_state:
        bot.send_message(chat_id, "Lütfen /start komutunu gönderin.")
        return

    # Cancel?
    if text.lower() in {BTN_CANCEL.lower(), '/cancel'}:
        handle_cancel(message)
        return

    step = user_state.get(chat_id)

    if step == 'animal':
        if text not in (BTN_CAT, BTN_DOG, BTN_BIRD):
            bot.send_message(chat_id, TXT_CHOOSE_ANIMAL, reply_markup=keyboard_animals())
            return
        user_data[chat_id]['Hayvan'] = text
        user_state[chat_id] = 'gender'
        bot.send_message(chat_id, TXT_CHOOSE_GENDER, reply_markup=keyboard_gender())
        return

    if step == 'gender':
        if text not in (BTN_MALE, BTN_FEMALE):
            bot.send_message(chat_id, TXT_CHOOSE_GENDER, reply_markup=keyboard_gender())
            return
        user_data[chat_id]['Cinsiyet'] = text
        user_state[chat_id] = 'age'
        bot.send_message(chat_id, TXT_ENTER_AGE, reply_markup=types.ReplyKeyboardRemove())
        return

    if step == 'age':
        # free text
        user_data[chat_id]['Yaş'] = text
        user_state[chat_id] = 'neuter'
        bot.send_message(chat_id, TXT_CHOOSE_NEUTER, reply_markup=keyboard_neuter())
        return

    if step == 'neuter':
        if text not in (BTN_NEUTERED, BTN_INTACT):
            bot.send_message(chat_id, TXT_CHOOSE_NEUTER, reply_markup=keyboard_neuter())
            return
        user_data[chat_id]['Kısırlaştırma'] = text
        user_state[chat_id] = 'complaint'
        bot.send_message(chat_id, TXT_ENTER_COMPLAINT, reply_markup=types.ReplyKeyboardRemove())
        return

    if step == 'complaint':
        user_data[chat_id]['Şikayet'] = text
        user_state[chat_id] = 'meds'
        bot.send_message(chat_id, TXT_ENTER_MEDS)
        return

    if step == 'meds':
        user_data[chat_id]['İlaçlar'] = text
        user_state[chat_id] = 'done'
        finalize_conversation(chat_id)
        return

    # fallback
    bot.send_message(chat_id, "Anlaşılmadı. /start ile tekrar deneyin.")


# ------------------------------------------------------------------
# Flask app / webhook
# ------------------------------------------------------------------
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'OK', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415


# ------------------------------------------------------------------
# Startup: ensure webhook is set (and polling is NOT used)
# ------------------------------------------------------------------
def ensure_webhook():
    if not WEBHOOK_URL:
        logging.warning("WEBHOOK_URL not set; bot will not receive updates!")
        return
    try:
        # remove old just in case, then set new
        bot.remove_webhook()
    except Exception as e:
        logging.warning("remove_webhook failed: %s", e)

    import time
    time.sleep(0.5)
    success = bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    if success:
        logging.info("Webhook set to %s", WEBHOOK_URL)
    else:
        logging.error("Failed to set webhook!")


# Render will run this module with gunicorn (see start command).
# But for local debugging: python main.py
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    ensure_webhook()
    # Local run: start Flask (do NOT start polling)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
