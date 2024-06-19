from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from environs import Env
import queue, sqlite3, logging
import asyncio
from datetime import datetime, timedelta

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
def create_booking_table():
    """Creates the booking table if it doesn't exist."""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS booking (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      day TEXT,
                      slot TEXT,
                      name TEXT
                      )""")
    conn.commit()
    conn.close()

create_booking_table()

""" Define a function to get the dates of the current week """
def get_week_dates_and_weekdays():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Get the latest Monday
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    return [(start_of_week + timedelta(days=i), weekdays[i]) for i in range(5)]

def get_todays_weekday():
    """Gets the weekday name for today's date."""
    today = datetime.now()
    weekday = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    return weekday[today.weekday()]  # Access by weekday number (0-6)

weekdays = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
timeslots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

""" create into the database draft schedule for next week, should be changed to create it automatically on a weekly basis """
def create_schedule():
    conn = sqlite3.connect('bookings.db')
    conn.execute("BEGIN TRANSACTION")
    cursor = conn.cursor()
    for day in weekdays:
        for slot in timeslots:
            cursor.execute(
                """INSERT INTO booking (day, slot, name) VALUES (?, ?, ?)""",
                (day, slot, "free")
            )
    conn.commit()
    conn.close()

# create_schedule()

""" Get today's schedule """

def get_today_schedule():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM booking WHERE day = ?""", (get_todays_weekday(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    schedule = "\n".join([f"{row[1]} {row[2]}: {row[3]}" for row in rows])
    return schedule

""" Get tomorrow's schedule """
def get_romorrow_schedule():
    pass

""" Get the schedule for the week """

def get_week_schedule():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM booking""")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    schedule = "\n".join([f"{row[1]} {row[2]}: {row[3]}" for row in rows])
    return schedule

def book_for_today():
    conn = sqlite3.connect('bookings.db')
    conn.execute("BEGIN TRANSACTION")
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE booking SET name = ? WHERE day = ? AND slot = ?""",
        ("booked", get_todays_weekday(), "08:00")
    )
    conn.commit()
    conn.close()

def get_name():
    while True:
        user_input = input().strip()
        if user_input and any(char.isalpha() for char in user_input):
            break
        else:
            print("Ім'я не повинно містити цифри")

    capitalized_name = user_input[0].upper() + user_input[1:].lower()

    return capitalized_name

""" Start the bot """

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [
        [ InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
        [ InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
        [ InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(reply_keyboard)

    await update.message.reply_text("виберіть опцію:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    if query.data == "1":
       schedule = get_today_schedule()
       reply_keyboard = [
           [ InlineKeyboardButton("Бронювати слот на сьогодні", callback_data="book_today")],
           [ InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
           [ InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
           ]
       reply_markup = InlineKeyboardMarkup(reply_keyboard)
       await query.message.reply_text(text=f"Сьогоднішній графік:\n{schedule}")
       await query.message.reply_text(text="Виберіть опцію:", reply_markup=reply_markup)
    
    elif query.data == "2":
        # Implement fetching and displaying tomorrow's schedule
        await query.message.reply_text(text="Завтрашній графік")
    
    elif query.data == "book_today":
        await query.message.reply_text(text=f"Введіть ім'я: {get_name}")
        await query.message.reply_text(text=f"Заброньовано")
    
    # elif query.data == "book_tomorrow":
    #     await query.edit_message_text(text=f"Заброньовано")

    else:
        await query.edit_message_text(text=f"Графік на тиждень:\n{get_week_schedule()}")

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
