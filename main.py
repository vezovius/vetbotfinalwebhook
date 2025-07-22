
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

WELCOME = 0
TUR = 1
CINSIYET = 2
YAS = 3
KISIR = 4
SIKAYET = 5
ILACLAR = 6

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    context.user_data["chat_id"] = chat_id
    context.user_data["data"] = {}
    await update.message.reply_text("🐾 Hoş geldiniz! Hayvanınızın bilgilerini toplamaya başlayalım.")
    reply_markup = ReplyKeyboardMarkup([["🐶 Köpek", "🐱 Kedi", "🐦 Kuş"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("1️⃣ Lütfen hayvanın türünü seçin:", reply_markup=reply_markup)
    return TUR

async def tur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["Tür"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["Erkek", "Dişi"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("2️⃣ Hayvanın cinsiyeti nedir?", reply_markup=reply_markup)
    return CINSIYET

async def cinsiyet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["Cinsiyet"] = update.message.text
    await update.message.reply_text("3️⃣ Hayvanın yaşı kaç?")
    return YAS

async def yas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["Yaş"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["Evet", "Hayır"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("4️⃣ Hayvan kısır mı?", reply_markup=reply_markup)
    return KISIR

async def kisir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["Kısır mı?"] = update.message.text
    await update.message.reply_text("5️⃣ Ana şikayet nedir?")
    return SIKAYET

async def sikayet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["Ana Şikayet"] = update.message.text
    await update.message.reply_text("6️⃣ Kullanılan ilaçları belirtin:")
    return ILACLAR

async def ilaclar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"]["İlaçlar"] = update.message.text
    data = load_data()
    chat_id = context.user_data["chat_id"]
    data[chat_id] = context.user_data["data"]
    save_data(data)
    await update.message.reply_text("✅ Bilgileriniz kaydedildi. Teşekkür ederiz!")
    return ConversationHandler.END

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, tur)],
            CINSIYET: [MessageHandler(filters.TEXT & ~filters.COMMAND, cinsiyet)],
            YAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, yas)],
            KISIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, kisir)],
            SIKAYET: [MessageHandler(filters.TEXT & ~filters.COMMAND, sikayet)],
            ILACLAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ilaclar)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
