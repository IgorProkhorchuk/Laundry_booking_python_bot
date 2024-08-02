from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, \
    MessageHandler, filters
from environs import Env
import queue, sqlite3, logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

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


# database path
global database_path
database_path = '/opt/laundry_db/bookings.db'


# initialize database
def create_booking_table():
    """Creates the booking table if it doesn't exist."""
    conn = sqlite3.connect(database_path)
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
    # Get the start of the current week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    if today.weekday() >= 5:
        start_of_week += timedelta(days=7)  # If today is Saturday or Sunday, get next Monday
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    return [(start_of_week + timedelta(days=i), weekdays[i]) for i in range(5)]


def get_todays_weekday():
    """Gets the weekday name for today's date."""
    today = datetime.now()
    weekday = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
    return weekday[today.weekday()]  # Access by weekday number (0-4)


def get_tomorrows_weekday():
    """Gets the weekday name for tomorrow's date."""
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    weekday = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
    return weekday[tomorrow.weekday()]  # Access by weekday number (0-4)


weekdays = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
timeslots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

""" create into the database draft schedule for next week, should be changed to create it automatically on a weekly basis """


def update_weekly_schedule():
    conn = sqlite3.connect(database_path)
    conn.execute("BEGIN TRANSACTION")
    cursor = conn.cursor()
    for day in weekdays:
        for slot in timeslots:
            cursor.execute('DROP TABLE booking')
            cursor.execute("""CREATE TABLE IF NOT EXISTS booking (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      day TEXT,
                      slot TEXT,
                      name TEXT
                      )""")
            cursor.execute(
                """INSERT INTO booking (day, slot, name) VALUES (?, ?, ?)""",
                (day, slot, "free")
            )
    conn.commit()
    conn.close()


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_weekly_schedule, trigger='cron', day_of_week='fri', hour=20)
scheduler.start()


""" Format the schedule for display """

def format_schedule(rows):
    header = f"{'День':<12}{'Час':<8}{'Ім"я':<12}\n"
    line = "-" * 32 + "\n"
    schedule = header + line + "\n".join([f"{row[1]:<12}{row[2]:<8}{row[3]:<12}" for row in rows])
    return schedule

""" Get today's schedule """


def get_today_schedule():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM booking WHERE day = ?""", (get_todays_weekday(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return format_schedule(rows)


""" Get tomorrow's schedule """


def get_romorrow_schedule():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM booking WHERE day = ?""", (get_tomorrows_weekday(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return format_schedule(rows)


""" Get the schedule for the week """


def get_week_schedule():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM booking""")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return format_schedule(rows)

def get_day_schedule(selected_day):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM booking WHERE day = ?""", (selected_day,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return format_schedule(rows)


def get_available_slots_today():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT slot FROM booking WHERE day = ? AND name = 'free'""", (get_todays_weekday(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    available_slots = [row[0] for row in rows]
    return available_slots


def get_available_slots_tomorrow():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT slot FROM booking WHERE day = ? AND name = 'free'""", (get_tomorrows_weekday(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    available_slots = [row[0] for row in rows]
    return available_slots



def get_available_slots_selected_day(selected_day):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT slot FROM booking WHERE day = ? AND name = 'free'""", (selected_day,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    available_slots = [row[0] for row in rows]
    return available_slots

""" Start the bot """


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [
        [InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
        [InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
        [InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(reply_keyboard)

    await update.message.reply_text("виберіть опцію:", reply_markup=reply_markup)

# Add a regular button for /start command
    start_button = [[KeyboardButton("На початок")]]
    start_reply_markup = ReplyKeyboardMarkup(start_button, one_time_keyboard=True, resize_keyboard=True)
    reply_markup=start_reply_markup



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "1":
        schedule = get_today_schedule()
        weekday = get_todays_weekday()
        reply_keyboard = [
            [InlineKeyboardButton("Бронювати слот на сьогодні", callback_data="book_today")],
            [InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
            [InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
            [InlineKeyboardButton("Назад", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await query.message.reply_text(text=f"Сьогоднішній графік:\n{weekday}\n{schedule}")
        await query.message.reply_text(text="Виберіть опцію:", reply_markup=reply_markup)

    elif query.data == "2":
        schedule = get_romorrow_schedule()
        weekday = get_tomorrows_weekday()
        reply_keyboard = [
            [InlineKeyboardButton("Бронювати слот на завтра", callback_data="book_tomorrow")],
            [InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
            [InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
            [InlineKeyboardButton("Назад", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await query.message.reply_text(text=f"Завтрашній графік:\n{weekday}\n{schedule}")
        await query.message.reply_text(text="Виберіть опцію:", reply_markup=reply_markup)

    elif query.data == "3":
        schedule = get_week_schedule()
        reply_keyboard = [
            [InlineKeyboardButton("Виберіть день  для бронювання: ", callback_data="select_day")],
            [InlineKeyboardButton("Назад", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await query.message.reply_text(text=f"Графік на тиждень:\n{schedule}")
        await query.message.reply_text(text="Виберіть опцію:", reply_markup=reply_markup)

    elif query.data == "book_today":
        available_slots = get_available_slots_today()
        if available_slots:
            context.user_data['booking_day'] = get_todays_weekday()
            reply_keyboard = [[InlineKeyboardButton(slot, callback_data=f"slot_{slot}")] for slot in available_slots]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            await query.message.reply_text(text="Виберіть доступний слот:", reply_markup=reply_markup)
        else:
            await query.message.reply_text(text="Немає доступних слотів на сьогодні.")

    elif query.data == "book_tomorrow":
        available_slots = get_available_slots_tomorrow()
        if available_slots:
            context.user_data['booking_day'] = get_tomorrows_weekday()
            reply_keyboard = [[InlineKeyboardButton(slot, callback_data=f"slot_{slot}")] for slot in available_slots]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            await query.message.reply_text(text="Виберіть доступний слот:", reply_markup=reply_markup)
        else:
            await query.message.reply_text(text="Немає доступних слотів на завтра.")

    elif query.data == "select_day":
        reply_keyboard = [[InlineKeyboardButton(day, callback_data=f"day_{day}")] for day in weekdays]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await query.message.reply_text(text="Виберіть день для бронювання:", reply_markup=reply_markup)

    elif query.data.startswith("day_"):
        selected_day = query.data.split("_")[1]
        available_slots = get_available_slots_selected_day(selected_day)
        if available_slots:
            context.user_data['booking_day'] = selected_day
            reply_keyboard = [[InlineKeyboardButton(slot, callback_data=f"slot_{slot}")] for slot in available_slots]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            schedule = get_day_schedule(selected_day)
            await query.message.reply_text(text=f"Графік на {selected_day}:\n{schedule}")
            await query.message.reply_text(text="Виберіть доступний слот:", reply_markup=reply_markup)
        else:
            await query.message.reply_text(text=f"Немає доступних слотів на {selected_day}.")

    elif query.data.startswith("slot_"):
        selected_slot = query.data.split("_")[1]
        context.user_data['selected_slot'] = selected_slot
        await query.message.reply_text(text="Введіть ім'я:")

    elif query.data == "start":
        reply_keyboard = [
            [InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
            [InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
            [InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
        ]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await query.message.reply_text("виберіть опцію:", reply_markup=reply_markup)

    # else:
    #     await query.edit_message_text(text=f"Графік на тиждень:\n{get_week_schedule()}")


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.message.text.strip()
    if any(char.isdigit() for char in name):
        await update.message.reply_text("Ім'я не повинно містити цифри. Спробуйте ще раз.")
        return

    capitalized_name = name[0].upper() + name[1:].lower()
    selected_slot = context.user_data.get('selected_slot')
    booking_day = context.user_data.get('booking_day')
    
    if selected_slot and booking_day:
        book_slot(booking_day, selected_slot, capitalized_name)
        await update.message.reply_text(f"Заброньовано слот {selected_slot} для {capitalized_name}")
        context.user_data['selected_slot'] = None
        context.user_data['booking_day'] = None


def book_slot(day, slot, name):
    conn = sqlite3.connect(database_path)
    conn.execute("BEGIN TRANSACTION")
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE booking SET name = ? WHERE day = ? AND slot = ?""",
        (name, day, slot)
    )
    conn.commit()
    conn.close()


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
