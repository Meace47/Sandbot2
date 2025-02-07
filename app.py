import os
import telegram
from flask import Flask, request

# Replace with your bot's token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = Bot(8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
# ✅ Set up Flask for handling webhooks
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming messages from Telegram."""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    # ✅ Extract chat ID and text message
    chat_id = update.message.chat.id
    text = update.message.text

    # ✅ Respond to "/start" command
    if text == "/start":
        bot.send_message(chat_id=chat_id, text="🚛 Welcome to SandBot! Type /help for commands.")

    return "OK", 200 # ✅ Return HTTP 200 response to Telegram

# ✅ Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)
