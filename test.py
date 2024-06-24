import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import main  # Assume your bot code is in a file named main.py

class TestTelegramBot(unittest.TestCase):

    @patch('main.create_booking_table')
    def setUp(self, mock_create_booking_table):
        main.create_booking_table()

    @patch('main.get_todays_weekday')
    def test_get_today_schedule(self, mock_get_todays_weekday):
        mock_get_todays_weekday.return_value = 'Понеділок'
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE booking (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, slot TEXT, name TEXT)""")
        cursor.execute("""INSERT INTO booking (day, slot, name) VALUES ('Понеділок', '08:00', 'free')""")
        conn.commit()
        main.get_today_schedule()

        cursor.execute("SELECT * FROM booking WHERE day = 'Понеділок'")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'Понеділок')
        self.assertEqual(rows[0][2], '08:00')
        self.assertEqual(rows[0][3], 'free')
        conn.close()

    @patch('main.get_todays_weekday')
    @patch('main.Update')
    @patch('main.ContextTypes.DEFAULT_TYPE')
    async def test_start_command(self, mock_context, mock_update, mock_get_todays_weekday):
        mock_get_todays_weekday.return_value = 'Понеділок'
        update = MagicMock()
        context = MagicMock()
        await main.start(update, context)

        update.message.reply_text.assert_called_once_with(
            "виберіть опцію:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Показати графік на сьогодні", callback_data="1")],
                [InlineKeyboardButton("Показати графік на завтра", callback_data="2")],
                [InlineKeyboardButton("Показати графік на тиждень", callback_data="3")],
            ])
        )

    @patch('main.get_today_schedule')
    @patch('main.get_todays_weekday')
    @patch('main.Update')
    @patch('main.ContextTypes.DEFAULT_TYPE')
    async def test_button_callback_today(self, mock_context, mock_update, mock_get_todays_weekday, mock_get_today_schedule):
        mock_get_today_schedule.return_value = "08:00: free"
        mock_get_todays_weekday.return_value = "Понеділок"
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "1"
        await main.button(update, context)

        query.message.reply_text.assert_called_with(
            text=f"Сьогоднішній графік:\nПонеділок\n08:00: free"
        )

    @patch('main.get_available_slots_today')
    @patch('main.get_todays_weekday')
    @patch('main.Update')
    @patch('main.ContextTypes.DEFAULT_TYPE')
    async def test_button_callback_book_today(self, mock_context, mock_update, mock_get_todays_weekday, mock_get_available_slots_today):
        mock_get_available_slots_today.return_value = ['08:00']
        mock_get_todays_weekday.return_value = 'Понеділок'
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "book_today"
        await main.button(update, context)

        query.message.reply_text.assert_called_with(
            text="Виберіть доступний слот:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('08:00', callback_data='slot_08:00')]
            ])
        )

if __name__ == '__main__':
    unittest.main()
