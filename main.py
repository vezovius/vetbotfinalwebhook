import os
import json
import logging
from datetime import datetime

from flask import Flask, request
import telebot
from telebot import types

"""
VetBot Webhook Version
----------------------
Conversation flow (all prompts in Turkish):

  1. Hayvan türü? [Kedi | Köpek | Kuş]
  2. Cinsiyet? [Erkek | Dişi | Bilinmiyor]
  3. Yaş grubu? [Yavru | Genç | Yetişkin | Yaşlı]
  4. Kısırlaştırılmış mı? [Evet | Hayır | Bilinmiyor]
  5. Ana şikayetiniz nedir? (serbest metin)
  6. Şu ana kadar kullanılan ilaçlar? (serbest metin)

Ardından özet mesajı ve teşekkür.
Kayıtlar data.json dosyasına (liste formatında) append edilir.
"""

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN ortam değişkeni tanımlı değil!")

DATA_FILE = os.getenv("DATA_FILE", "data.json")

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("vetbot")

# ------------------------------------------------------------------
# Telegram Bot setup (webhook mode)
# ------------------------------------------------------------------
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=False)

# user_state: chat_id -> {"step": int, "data": {...}}
user_state = {}

# Utility: ensure persistent json list
def _load_records():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error("data.json yüklenemedi: %s", e)
        return []

def _save_record(record: dict):
    records = _load_records()
    records.append(record)
    # keep file size reasonable (optional: limit to last N)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error("data.json yazılamadı: %s", e)

# ------------------------------------------------------------------
# Conversation helpers
# ------------------------------------------------------------------
def send_animal_type(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("Kedi", "Köpek", "Kuş")
    bot.send_message(chat_id, "Hayvan türünü seçiniz:", reply_markup=markup)

def send_gender(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("Erkek", "Dişi", "Bilinmiyor")
    bot.send_message(chat_id, "Cinsiyetini seçiniz:", reply_markup=markup)

def send_age(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("Yavru", "Genç")
    markup.row("Yetişkin", "Yaşlı")
    bot.send_message(chat_id, "Yaş grubunu seçiniz:", reply_markup=markup)

def send_neuter(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("Evet", "Hayır", "Bilinmiyor")
    bot.send_message(chat_id, "Kısırlaştırılmış mı?", reply_markup=markup)

def ask_complaint(chat_id):
    hide = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Ana şikayetiniz nedir? Lütfen yazınız.", reply_markup=hide)

def ask_drugs(chat_id):
    hide = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Şu ana kadar kullanılan ilaçlar? (Yoksa 'Yok' yazın.)", reply_markup=hide)

def finish_and_save(chat_id):
    # Compose summary text
    data = user_state[chat_id]["data"]
    summary_lines = [
        "Teşekkürler. Alınan bilgiler:",
        f"- Hayvan türü: {data.get('hayvan_turu','?')}",
        f"- Cinsiyet: {data.get('cinsiyet','?')}",
        f"- Yaş grubu: {data.get('yas','?')}",
        f"- Kısırlaştırma: {data.get('kisir','?')}",
        f"- Ana şikayet: {data.get('sikayet','?')}",
        f"- Kullanılan ilaçlar: {data.get('ilaclar','?')}",
    ]
    bot.send_message(chat_id, "\n".join(summary_lines))

    # Persist
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "chat_id": chat_id,
        **data,
    }
    _save_record(record)

    # cleanup state
    user_state.pop(chat_id, None)

# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------
@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {"step": 1, "data": {}}
    bot.send_message(chat_id, "Merhaba! Ben veteriner asistan botuyum. Lütfen soruları yanıtlayınız.")
    send_animal_type(chat_id)

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_all_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_state:
        # Not in conversation; instruct user to /start
        bot.send_message(chat_id, "Lütfen /start komutuyla başlayınız.")
        return

    step = user_state[chat_id]["step"]
    data = user_state[chat_id]["data"]

    if step == 1:
        data["hayvan_turu"] = text
        user_state[chat_id]["step"] = 2
        send_gender(chat_id)
    elif step == 2:
        data["cinsiyet"] = text
        user_state[chat_id]["step"] = 3
        send_age(chat_id)
    elif step == 3:
        data["yas"] = text
        user_state[chat_id]["step"] = 4
        send_neuter(chat_id)
    elif step == 4:
        data["kisir"] = text
        user_state[chat_id]["step"] = 5
        ask_complaint(chat_id)
    elif step == 5:
        data["sikayet"] = text
        user_state[chat_id]["step"] = 6
        ask_drugs(chat_id)
    elif step == 6:
        data["ilaclar"] = text
        finish_and_save(chat_id)
    else:
        bot.send_message(chat_id, "Lütfen /start komutuyla yeni bir form başlatınız.")

# ------------------------------------------------------------------
# Flask app / Webhook integration
# ------------------------------------------------------------------
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return "I'm alive!", 200

@app.route(f"/bot{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    else:
        log.warning("Unknown content type: %s", request.headers.get("content-type"))
    return "OK", 200

# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    log.info("Starting Flask on 0.0.0.0:%s", port)
    # Important: do NOT call bot.polling(), we run in webhook mode.
    app.run(host="0.0.0.0", port=port)
