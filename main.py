import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = "7776065669:AAEWGA0PI1Hs0NwuNTRQUGU8Atkeuhbetdg"  # <-- Replace this with your bot token

bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return 'Vetbot Webhook is active!'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok', 200

def start(update, context):
    update.message.reply_text("Merhaba! Ben veteriner botunuzum. Size nasıl yardımcı olabilirim?")

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler('start', start))
