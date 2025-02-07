import os
import telegram
from flask import Flask, request

# ✅ Load the bot token from Railway's environment variables
TOKEN = os.getenv("BOT_TOKEN")

# ✅ Debugging: Print the token only if it exists, otherwise show an error
if TOKEN:
    print(f"🔍 Debug Token Loaded Successfully") # 🚀 Safe debugging
else:
    print("❌ ERROR: BOT_TOKEN is not loaded! Check Railway Variables.")

# ✅ Initialize the bot
bot = telegram.Bot(token=TOKEN)

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
