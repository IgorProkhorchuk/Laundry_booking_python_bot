from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from environs import Env
import queue, sqlite3, logging
import asyncio


# Load the environment variables
env = Env()
env.read_env()

TOKEN = env('TOKEN')
BOT_USERNAME = env('BOT_USERNAME')

logfile_path = 'logs.log'
# Enable logging
logging.basicConfig(
    filename=logfile_path,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# initialize database

conn = sqlite3.connect('bookings.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS booking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT,
                    slot TEXT,
                    name TEXT
                    )
               """)
conn.commit()
conn.close()

# Define the start command handler

# GENDER, PHOTO, LOCATION, BIO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [ InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
        [ InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
        [ InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(reply_keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

    # await update.message.reply_text(
    #     "Hi! My name is Professor Bot. I will hold a conversation with you. "
    #     "Send /cancel to stop talking to me.\n\n"
    #     "Are you a boy or a girl?",
    #     reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    # )

    # return GENDER





if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()