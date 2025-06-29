from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
REQUIRED_CHANNELS = os.environ.get("REQUIRED_CHANNELS", "").split()

joined_users = set()

def check_user_joined(update: Update):
    user_id = update.effective_user.id
    for channel in REQUIRED_CHANNELS:
        try:
            member = update.effective_chat.get_member(user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not check_user_joined(update):
        buttons = [[InlineKeyboardButton("📢 Join All Channels", url=f"https://t.me/{ch[1:]}")]
                   for ch in REQUIRED_CHANNELS]
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=chat_id, text="Please join all channels first to use the bot:", reply_markup=reply_markup)
        return

    if user.id not in joined_users:
        joined_users.add(user.id)

    context.bot.send_message(chat_id=chat_id, text=f"👋 Welcome {user.first_name}!\n👥 Monthly Users: {len(joined_users)}")

def check(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if check_user_joined(query):
        if query.from_user.id not in joined_users:
            joined_users.add(query.from_user.id)
        query.edit_message_text(text=f"✅ Access Granted!\n👥 Monthly Users: {len(joined_users)}")
    else:
        query.edit_message_text("❌ You still need to join all channels.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check, pattern="check"))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
