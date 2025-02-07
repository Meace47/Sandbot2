from flask import Flask, request
import telegram
import os

# Load token
TOKEN = os.getenv("8029048707:AAGfxjlxZAIPkPS93a9BZ9w-Ku8-ywT5I-M") # If using Railway env variable
print(f"🔍 Debug Token: {TOKEN}") # Debugging output

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
