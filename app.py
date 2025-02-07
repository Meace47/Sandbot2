from flask import Flask, request
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Dispatcher
import os

TOKEN = "8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming Telegram messages via webhook"""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK', 200

def start(update, context):
    """Start command"""
    update.message.reply_text("Hello! SandBot is online.")

def help_command(update, context):
    """Help command"""
    update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show this help message")

def echo(update, context):
    """Echo all user messages"""
    update.message.reply_text(update.message.text)

if __name__ == "__main__":
    # Set up the bot
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, echo))

    # Set webhook for Flask
    PORT = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=f"https://your-hostname.com/{TOKEN}")

    app.run(host="0.0.0.0", port=PORT, debug=True)
