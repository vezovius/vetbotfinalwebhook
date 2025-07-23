import os
import json
from datetime import datetime
from flask import Flask, request, abort

import telebot
from telebot import types

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Environment variable BOT_TOKEN is required.")

WEBHOOK_SECRET_PATH = "/" + BOT_TOKEN  # Telegram will POST here

DATA_FILE = "data.json"  # stored in container; ephemeral on free tier

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)  # no Markdown to avoid escaping hassles

# ------------------------------------------------------------------
# Simple persistence helpers
# ------------------------------------------------------------------
def load_records():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_record(rec: dict):
    data = load_records()
    data.append(rec)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("WARN: could not save record:", e, flush=True)

# ------------------------------------------------------------------
# Conversation state (in‑memory; resets on redeploy)
# ------------------------------------------------------------------
user_state = {}
# keys: chat_id -> dict(fields..., step)

STEPS = ["animal", "sex", "age", "neutered", "complaint", "meds"]

ANIMALS = ["Kedi", "Köpek", "Kuş"]
SEXES = ["Erkek", "Dişi", "Bilmiyorum"]
AGES = ["Yavru", "Genç", "Yetişkin", "Yaşlı"]
NEUTERED = ["Kısır", "Kısır değil", "Bilmiyorum"]

# ------------------------------------------------------------------
# /start handler
# ------------------------------------------------------------------
@bot.message_handler(commands=["start"])
def cmd_start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {"step": "animal"}
    send_animal_q(chat_id)

# ------------------------------------------------------------------
# Step askers
# ------------------------------------------------------------------
def send_animal_q(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(*ANIMALS)
    bot.send_message(chat_id, "Hayvan türünü seçiniz:", reply_markup=markup)

def send_sex_q(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(*SEXES)
    bot.send_message(chat_id, "Cinsiyeti nedir?", reply_markup=markup)

def send_age_q(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(*AGES)
    bot.send_message(chat_id, "Yaş grubu nedir?", reply_markup=markup)

def send_neuter_q(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(*NEUTERED)
    bot.send_message(chat_id, "Hayvan kısır mı?", reply_markup=markup)

def send_complaint_q(chat_id):
    markup = types.ForceReply(selective=False)
    bot.send_message(chat_id, "Ana şikayet nedir? (Yazınız)", reply_markup=markup)

def send_meds_q(chat_id):
    markup = types.ForceReply(selective=False)
    bot.send_message(chat_id, "Şimdiye kadar kullanılan ilaçlar? (Yazınız)", reply_markup=markup)

# ------------------------------------------------------------------
# Generic text handler that routes by step
# ------------------------------------------------------------------
@bot.message_handler(content_types=["text"])
def collect_steps(message):
    chat_id = message.chat.id
    txt = (message.text or "").strip()

    if chat_id not in user_state:
        # unexpected text -> start new session
        user_state[chat_id] = {"step": "animal"}
        send_animal_q(chat_id)
        return

    state = user_state[chat_id]
    step = state.get("step")

    if step == "animal":
        state["animal"] = txt
        state["step"] = "sex"
        send_sex_q(chat_id)
        return

    if step == "sex":
        state["sex"] = txt
        state["step"] = "age"
        send_age_q(chat_id)
        return

    if step == "age":
        state["age"] = txt
        state["step"] = "neutered"
        send_neuter_q(chat_id)
        return

    if step == "neutered":
        state["neutered"] = txt
        state["step"] = "complaint"
        send_complaint_q(chat_id)
        return

    if step == "complaint":
        state["complaint"] = txt
        state["step"] = "meds"
        send_meds_q(chat_id)
        return

    if step == "meds":
        state["meds"] = txt
        state["step"] = "done"
        finish_chat(chat_id)
        return

    # If done, ignore or restart
    if step == "done":
        bot.send_message(chat_id, "Yeni bir değerlendirme başlatmak için /start yazınız.")
        return

# ------------------------------------------------------------------
def finish_chat(chat_id):
    state = user_state.get(chat_id, {})
    state["timestamp"] = datetime.utcnow().isoformat() + "Z"
    # Save
    save_record({**state, "chat_id": chat_id})
    # Summary
    summary_lines = [
        f"Hayvan: {state.get('animal','-')}",
        f"Cinsiyet: {state.get('sex','-')}",
        f"Yaş: {state.get('age','-')}",
        f"Kısır: {state.get('neutered','-')}",
        f"Şikayet: {state.get('complaint','-')}",
        f"İlaçlar: {state.get('meds','-')}",
    ]
    bot.send_message(chat_id, "Teşekkürler. Alınan bilgiler:\n" + "\n".join(summary_lines))
    bot.send_message(chat_id, "Yeni bir form için /start yazabilirsiniz.")
    # Stay done
    user_state[chat_id] = {"step": "done"}

# ------------------------------------------------------------------
# Flask routes
# ------------------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    return "VetBot webhook is running.", 200

@app.route(WEBHOOK_SECRET_PATH, methods=["POST"])
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        abort(403)

# ------------------------------------------------------------------
# Auto set webhook (optional)
# ------------------------------------------------------------------
def ensure_webhook():
    base_url = os.environ.get("WEBHOOK_BASE_URL")
    if not base_url:
        print("INFO: WEBHOOK_BASE_URL not set; not calling set_webhook().", flush=True)
        return
    full_url = base_url.rstrip("/") + WEBHOOK_SECRET_PATH
    try:
        bot.remove_webhook()
        bot.set_webhook(url=full_url, max_connections=40, allowed_updates=["message"])
        print(f"Webhook set to {full_url}", flush=True)
    except Exception as e:
        print("ERROR setting webhook:", e, flush=True)

ensure_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ensure_webhook()
    print(f"Running Flask dev server on port {port}...", flush=True)
    app.run(host="0.0.0.0", port=port)
