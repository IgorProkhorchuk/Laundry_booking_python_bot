import sqlite3

def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS booking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT,
                slot TEXT,
                name TEXT
            )
        ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

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


create_schedule()