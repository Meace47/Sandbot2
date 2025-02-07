"""Show the main menu options for drivers and admins."""
    user_id = update.message.from_user.id
    is_admin = user_id in ADMIN_IDS
    if is_admin:
        keyboard = [
            [InlineKeyboardButton("📋 View Staged Trucks", callback_data="view_staged")],
            [InlineKeyboardButton("🚛 Move Truck to Well", callback_data="move_to_well")],
            [InlineKeyboardButton("❌ Remove Truck", callback_data="remove_truck")],
            [InlineKeyboardButton("⚙️ Set Well Capacity", callback_data="set_well_capacity")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔧 *Admin Panel:*", reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("🚛 Stage My Truck", callback_data="stage")],
            [InlineKeyboardButton("📍 Check My Status", callback_data="status")],
            [InlineKeyboardButton("🏁 Leave the Well", callback_data="leave_well")],
            [InlineKeyboardButton("🔄 Change Truck Number", callback_data="change_truck")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚚 *Choose an action:*", reply_markup=reply_markup)

# 📌 **Admin: View Staged Trucks**
async def view_staged(update: Update, context):
    """Admins can view all staged trucks."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("❌ You are not an admin!")
        return

    if not staged_trucks:
        await query.edit_message_text("🚛 No trucks are currently staged.")
    else:
        staged_list = "\n".join([f"#{i+1} - Truck {num}" for i, (tid, num) in enumerate(staged_trucks)])
        await query.edit_message_text(f"📋 *Staged Trucks:*\n{staged_list}")

# 📌 **Admin: Move Truck to Well**
async def move_to_well(update: Update, context):
    """Admins move the next truck in line to the well."""
    query = update.callback_query

    if not staged_trucks:
        await query.edit_message_text("🚛 No trucks available to move to the well.")
        return

    truck = staged_trucks.pop(0)
    well_trucks.append(truck)
    await query.edit_message_text(f"🚛 *Truck {truck[1]} has been moved to the well!*")

# 📌 **Admin: Remove Truck**
async def remove_truck(update: Update, context):
    """Admins remove a specific truck from the list."""
    query = update.callback_query

    if not staged_trucks and not well_trucks:
        await query.edit_message_text("🚛 No trucks to remove.")
        return

    keyboard = [[InlineKeyboardButton(f"❌ Remove Truck {num}", callback_data=f"delete_{tid}")]
                for tid, num in staged_trucks + well_trucks]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("❌ *Select a truck to remove:*", reply_markup=reply_markup)

# 📌 **Admin: Set Well Capacity**
async def set_well_capacity(update: Update, context):
    """Admins set the number of trucks at the well."""
    query = update.callback_query
    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"set_limit_{i}")] for i in range(1, 6)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("⚙️ *Set the maximum number of trucks at the well:*", reply_markup=reply_markup)

async def update_well_limit(update: Update, context):
    """Update the well limit based on admin selection."""
    query = update.callback_query
    global truck_well_limit
    truck_well_limit = int(query.data.split("_")[2])
    await query.edit_message_text(f"🚛 The well will now hold up to {truck_well_limit} trucks.")

# 📌 **AI Response for General Questions**
async def ai_assistant(update: Update, context):
    """AI-powered responses for non-command messages."""
    responses = [
        "🤔 I'm not sure, but an admin might be able to help.",
        "🚛 If you need to stage or check status, use the buttons.",
        "📋 If this is urgent, please contact an admin."
    ]
    await update.message.reply_text(random.choice(responses))
    from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os
import logging
import random

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc"
WEBHOOK_URL = "https://sandbot2-production.up.railway.app.com"  # Replace with your actual Railway URL
USE_WEBHOOK = True  # Enable webhook mode

# Initialize Flask
app = Flask(__name__)

# Initialize Telegram Bot Application
bot_app = Application.builder().token(TOKEN).build()

# Data storage for truck information
truck_numbers = {}  # {user_id: truck_number}
staged_trucks = []  # List of (user_id, truck_number)
well_trucks = []  # List of (user_id, truck_number)
truck_well_limit = 5  # Default limit (admin can change)

# Admin List (Replace with actual admin Telegram IDs)
ADMIN_IDS = [5767285152]  # Replace with real admin IDs

# 📌 **Webhook Route**
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming Telegram messages via webhook."""
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.process_update(update)
    return "OK", 200

# 📌 **Prompt for Truck Number on First Message**
async def new_message(update: Update, context):
    """Prompt users to enter their truck number when they first send a message."""
    user_id = update.message.from_user.id
    if user_id not in truck_numbers:
        await update.message.reply_text("🚛 Please enter your truck number to proceed.")
    else:
        await show_main_menu(update, context)

# 📌 **Register Truck Number**
async def register_truck(update: Update, context):
    """Register or change a truck number when a driver sends their number."""
    user_id = update.message.from_user.id
    truck_number = update.message.text.strip()

    if not truck_number.isdigit():
        await update.message.reply_text("❌ Please enter a valid truck number.")
        return

    truck_numbers[user_id] = truck_number
    await update.message.reply_text(f"✅ Truck number {truck_number} registered!")
    await show_main_menu(update, context)

# 📌 **Show Main Menu**
async def show_main_menu(update: Update, context):
    """Show the main menu options for drivers."""
    keyboard = [
        [InlineKeyboardButton("🚛 Stage My Truck", callback_data="stage")],
        [InlineKeyboardButton("📍 Check My Status", callback_data="status")],
        [InlineKeyboardButton("🏁 Leave the Well", callback_data="leave_well")],
        [InlineKeyboardButton("🔄 Change Truck Number", callback_data="change_truck")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚚 *Choose an action:*", reply_markup=reply_markup)

# 📌 **Change Truck Number**
async def change_truck(update: Update, context):
    """Allow drivers to change their truck number."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in truck_numbers:
        del truck_numbers[user_id]  # Remove old truck number
    await query.answer()
    await query.edit_message_text("🔄 Please enter your new truck number.")

# 📌 **Stage Truck**
async def stage_truck(update: Update, context):
    """Move a truck to the staged list."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in truck_numbers:
        await query.answer("❌ You must enter your truck number first!")
        return

    truck_number = truck_numbers[user_id]

    if (user_id, truck_number) in staged_trucks:
        await query.answer("❌ You are already staged.")
        return

    staged_trucks.append((user_id, truck_number))  # Add to staged list
    await query.answer("✅ You have been staged.")
    await query.edit_message_text(f"🚛 Truck {truck_number} has been staged at position #{len(staged_trucks)}.")

    # Check if trucks need to be moved to the well
    await manage_well()

# 📌 **Check Status**
async def check_status(update: Update, context):
    """Allow drivers to check their current status."""
    query = update.callback_query
    user_id = query.from_user.id
    truck_number = truck_numbers.get(user_id, "Unknown")

    status_message = "❌ You are not staged."
    for i, (tid, num) in enumerate(staged_trucks, start=1):
        if tid == user_id:
            status_message = f"📍 You are staged at position #{i}."
            break

    for i, (tid, num) in enumerate(well_trucks, start=1):
        if tid == user_id:
            status_message = f"🚛 You are at the well, position #{i}."
            break

    await query.answer()
    await query.edit_message_text(status_message)

# 📌 **Leave Well**
async def leave_well(update: Update, context):
    """Allow a truck to leave the well."""
    query = update.callback_query
    user_id = query.from_user.id

    if (user_id, truck_numbers.get(user_id, "Unknown")) in well_trucks:
        well_trucks.remove((user_id, truck_numbers[user_id]))
        await query.answer("✅ You have left the well.")
        await query.edit_message_text("🏁 You have successfully left the well.")
        await manage_well()  # Move another truck to the well if needed
    else:
        await query.answer("❌ You are not at the well.")

# 📌 **Manage Well (Automatic Truck Movement)**
async def manage_well():
    """Ensure the correct number of trucks are at the well."""
    while len(well_trucks) < truck_well_limit and staged_trucks:
        truck = staged_trucks.pop(0)  # Move first in line
        well_trucks.append(truck)

# 📌 **AI Response for General Questions**
async def ai_assistant(update: Update, context):
    """AI-powered responses for non-command messages."""
    responses = [
        "🤔 I'm not sure, but an admin might be able to help.",
        "🚛 If you need to stage or check status, use the buttons.",
        "📋 If this is urgent, please contact an admin."
    ]
    await update.message.reply_text(random.choice(responses))

# 📌 **Handlers**
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_message))
bot_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), register_truck))
bot_app.add_handler(CallbackQueryHandler(stage_truck, pattern="stage"))
bot_app.add_handler(CallbackQueryHandler(check_status, pattern="status"))
bot_app.add_handler(CallbackQueryHandler(leave_well, pattern="leave_well"))
bot_app.add_handler(CallbackQueryHandler(change_truck, pattern="change_truck"))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_assistant))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_message))
bot_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), register_truck))
bot_app.add_handler(CallbackQueryHandler(view_staged, pattern="view_staged"))
bot_app.add_handler(CallbackQueryHandler(move_to_well, pattern="move_to_well"))
bot_app.add_handler(CallbackQueryHandler(remove_truck, pattern="remove_truck"))
bot_app.add_handler(CallbackQueryHandler(set_well_capacity, pattern="set_well_capacity"))
bot_app.add_handler(CallbackQueryHandler(update_well_limit, pattern="set_limit_.*"))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_assistant))

# 📌 **Start Webhook on Railway**
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{https://sandbot2-production.up.railway.app}.com/{TOKEN}"
    )
    app.run(host="0.0.0.0", port=PORT, debug=True)

