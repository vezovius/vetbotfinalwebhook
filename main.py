from flask import Flask, request
import telegram

TOKEN = "YOUR_TOKEN"
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telegram.Update.de_json(eval(json_str), bot)
    bot.send_message(chat_id=update.message.chat_id, text="پیام دریافت شد!")
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
