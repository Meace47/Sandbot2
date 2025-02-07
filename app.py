from flask import Flask, request
import telegram
import os

# ✅ Debugging: Check if Railway is reading the token
TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    print("❌ ERROR: BOT_TOKEN is not loaded from environment variables!")

else:
    print(f"✅ Debug Token: {8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc}")  # This should show the actual token

# Initialize bot
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route("https://sandbot2-production.up.railway.app/webhook", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text
    
    if text == "/start":
        bot.send_message(chat_id=chat_id, text="Hello! I'm your bot.")
    
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
