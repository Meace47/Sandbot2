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
WEBHOOK_URL = "https://your-railway-url.com" # Replace with your actual Railway URL
USE_WEBHOOK = True # Enable webhook mode

# Initialize Flask
app = Flask(__name__)

# Initialize Telegram Bot Application
bot_app = Application.builder().token(TOKEN).build()

# Data storage for truck information
truck_numbers = {} # {user_id: truck_number}
staged_trucks = [] # List of (user_id, truck_number)
well_trucks = [] # List of (user_id, truck_number)
truck_well_limit = 5 # Default limit (admin can change)

# Admin List (Replace with actual admin Telegram IDs)
ADMIN_IDS = [5767285152] # Replace with real admin IDs

# 📌 **Webhook Route**
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming Telegram messages via webhook."""
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.process_update(update)
    return "OK", 200

async def start(update: Update, context):
    """Welcome message and menu display."""
    await update.message.reply_text("👋 Welcome! Choose an action below:", reply_markup=driver_menu)

# 📌 **Prompt for Truck Number on First Message**
async def new_message(update: Update, context):
     """Prompt new users to press 'Start' before continuing."""
    user_id = update.message.from_user.id

    if user_id in truck_numbers and truck_numbers[user_id]:  # If truck number exists, show main menu
        await show_main_menu(update, context)
    else:
        await update.message.reply_text("🚛 Welcome! Press 'Start' to continue.", reply_markup=start_menu)

async def handle_start_button(update: Update, context):
    """Handles when a user presses 'Start'."""
    user_id = update.message.from_user.id

    if user_id in truck_numbers:
        await show_main_menu(update, context)  # Show the main menu if they already have a truck number
    else:
        await update.message.reply_text("🚛 Please enter your truck number to proceed.")

# 📌 **Register Truck Number**
async def register_truck(update: Update, context):
    user_id = update.message.from_user.id
    truck_number = update.message.text.strip()

    if not truck_number.isdigit():
        await update.message.reply_text("❌ Please enter a valid truck number.")
        return

    # ✅ Save the truck number only if it's valid
    truck_numbers[user_id] = truck_number 

    await update.message.reply_text(f"✅ Truck number {truck_number} registered successfully!")
   
    # ✅ Move directly to the main menu after registration
    await show_main_menu(update, context)

    if not truck_number.isdigit():
        await update.message.reply_text("❌ Please enter a valid truck number.")
        return

    truck_numbers[user_id] = truck_number
    await update.message.reply_text(f"✅ Truck number {truck_number} registered!")
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context):
    """Show the menu to drivers and admins."""
    user_id = update.message.from_user.id

    if user_id in ADMIN_IDS:
        await update.message.reply_text("🔧 *Admin Panel Available!*", reply_markup=menu_markup)
    else:
        await update.message.reply_text("🚚 *Choose an action:*", reply_markup=menu_markup)

async def handle_menu_buttons(update: Update, context):
    """Handles button presses from the persistent menu."""
    text = update.message.text

    if text == "🚛 Stage My Truck":
        await stage_truck(update, context)
    elif text == "📍 Check My Status":
        await check_status(update, context)
    elif text == "🏁 Leave the Well":
        await leave_well(update, context)
    elif text == "🔄 Change Truck Number":
        await change_truck(update, context)
    elif text == "🔧 Admin Panel" and update.message.from_user.id in ADMIN_IDS:
        await show_main_menu(update, context)
    else:
        await update.message.reply_text("❌ Invalid option. Please choose from the menu.")


# 📌 **Show Main Menu**
async def show_main_menu(update: Update, context):
    user_id = update.message.from_user.id
    is_admin = user_id in ADMIN_IDS

    print(f"User {user_id} is admin: {is_admin}") # Debugging line

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
        await update.message.reply_text("Sandbot 2 Staging system!")
        keyboard = [
            [InlineKeyboardButton("🚛 Stage My Truck", callback_data="stage")],
            [InlineKeyboardButton("📍 Check My Status", callback_data="status")],
            [InlineKeyboardButton("🏁 Leave the Well", callback_data="leave_well")],
            [InlineKeyboardButton("🔄 Change Truck Number", callback_data="change_truck")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚚 *Choose an action:*", reply_markup=reply_markup)

async def remove_truck(update: Update, context):
    """Admins remove a specific truck from the list."""
    query = update.callback_query

    if not staged_trucks and not well_trucks:
        await query.answer("🚛 No trucks to remove.")
        return

    # Create a list of buttons for admins to select a truck to remove
    keyboard = [[InlineKeyboardButton(f"❌ Remove Truck {num}", callback_data=f"delete_{tid}")]
                for tid, num in staged_trucks + well_trucks]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("❌ *Select a truck to remove:*", reply_markup=reply_markup)

# Handle truck deletion when an admin selects one
async def delete_truck(update: Update, context):
    """Remove a truck when an admin selects it from the list."""
    query = update.callback_query
    truck_id = query.data.split("_")[1]  # Extract truck ID

    global staged_trucks, well_trucks
    staged_trucks = [(tid, num) for tid, num in staged_trucks if str(tid) != truck_id]
    well_trucks = [(tid, num) for tid, num in well_trucks if str(tid) != truck_id]

    await query.answer("✅ Truck removed successfully.")
    await query.edit_message_text("🚛 Truck has been removed.")

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

    staged_trucks.append((user_id, truck_number)) # Add to staged list
    await query.answer("✅ You have been staged.")
    await query.edit_message_text(f"🚛 Truck {truck_number} has been staged at position #{len(staged_trucks)}.")

    # Check if trucks need to be moved to the well
    await manage_well(update, context)

async def move_to_well(update: Update, context):
    """Admins move the next truck in line to the well."""
    query = update.callback_query

    if not staged_trucks:
        await query.answer("🚛 No trucks available to move to the well.")
        return

    truck = staged_trucks.pop(0)  # Move first in line
    well_trucks.append(truck)

    await query.answer(f"✅ Truck {truck[1]} has been moved to the well!")
    await query.edit_message_text(f"🚛 *Truck {truck[1]} has been moved to the well!*")

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

# 📌 **Manage Well (Auto Truck Movement & Notify Admin If Full)**
async def manage_well(update: Update, context):
    """Ensure the correct number of trucks are at the well and notify the admin if full."""
    while len(well_trucks) < truck_well_limit and staged_trucks:
        truck = staged_trucks.pop(0) # Move first in line
        well_trucks.append(truck)

    if len(well_trucks) >= truck_well_limit:
        # Notify Admins if the well is full
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id, text="⚠️ The well is full! Move trucks or increase the limit.")

# 📌 **Admin: Set Well Capacity**
async def set_well_capacity(update: Update, context):
    """Admins set the number of trucks at the well."""
    query = update.callback_query
    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"set_limit_{i}")] for i in range(1, 11)]
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

async def view_staged(update: Update, context):
    query = update.callback_query
    await query.answer("✅ Viewing staged trucks...")
    await query.edit_message_text("📋 Staged truck list goes here.")

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# "Start" button for new drivers
start_keyboard = [
    ["▶️ Start"]
]

# Convert to ReplyKeyboardMarkup
start_menu = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True, one_time_keyboard=True)

# Persistent menu keyboard
menu_keyboard = [
    ["🚛 Stage My Truck", "📍 Check My Status"],
    ["🏁 Leave the Well", "🔄 Change Truck Number"],
]

# Admin panel option (Admins will see this added button)
admin_menu_keyboard = [
    ["🚛 Stage My Truck", "📍 Check My Status"],
    ["🏁 Leave the Well", "🔄 Change Truck Number"],
    ["🔧 Admin Panel"]  # Only available for admins
]

# Convert menu into ReplyKeyboardMarkup (always visible)
driver_menu = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=False)
admin_menu = ReplyKeyboardMarkup(admin_menu_keyboard, resize_keyboard=True, one_time_keyboard=False)

# 📌 **Handlers**

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'▶️ Start'), handle_start_button))
bot_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), register_truck))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_message))
bot_app.add_handler(CallbackQueryHandler(view_staged, pattern="view_staged"))
bot_app.add_handler(CallbackQueryHandler(move_to_well, pattern="move_to_well"))
bot_app.add_handler(CallbackQueryHandler(remove_truck, pattern="remove_truck"))
bot_app.add_handler(CallbackQueryHandler(stage_truck, pattern="stage"))
bot_app.add_handler(CallbackQueryHandler(stage_truck, pattern="delete_.*"))
bot_app.add_handler(CallbackQueryHandler(check_status, pattern="status"))
bot_app.add_handler(CallbackQueryHandler(set_well_capacity, pattern="set_well_capacity"))
bot_app.add_handler(CallbackQueryHandler(update_well_limit, pattern="set_limit_.*"))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_assistant))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_main_menu))

if __name__ == "__main__":
    bot_app.run_polling()
