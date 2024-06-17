# Task Decomposition

#### Start bot option

- Button `/start` bot should show three options (buttons):
    - `/display_today_schedule`
    - `/display_tomorrow_schedule`
    - `/display_this_week_schedule`
> _done_


##### Create Database to store the booking results
> _done_

##### Display today schedule

- should be displayed an ordered list with timeslots for starts with "1" with actual schedule for **today**
    - if timeslot is already booked by someone -- should be displayed time and Name of person who booked this timeslot in the right of time (ex. __"09:00 - *Ivan*"__)
    - if timeslot is free -- should be displayed time and a word "free" (ex. __"09:00 - *free*"__)
    - button `/book_for_today` should be displayed
    - button `/book_for_other_day` should be displayed
    - button `/start` should be displayed

##### Display tomorrow schedule

- should be displayed an ordered list with timeslots for starts with "1" with actual schedule for **tomorrow**
    - if timeslot is already booked by someone -- should be displayed time and Name of person who booked this timeslot in the right of time (ex. __"09:00 - *Ivan*"__)
    - if timeslot is free -- should be displayed time and a word "free" (ex. __"09:00 - *free*"__)
    - button `/book_for_tomorrow` should be displayed
    - button `/book_for_other_day` should be displayed
    - button `/start` should be displayed

##### Display week schedule

- should be displayed week days (from Monday to Friday) with ordered list with actual timeslots under each weekday respectively.
    - if timeslot is already booked by someone -- timeslot should be displayed in dark red color; if timeslot is free -- timeslot should be displayed in green color;


#### Book option

- Button `/book` should redirect to next options:
    - `/book_for_today` -- when person select /book_for_today 
    - `/book_for_tomorrow`
    - `/book_for_other_day`
        - Button `/book_for_other_day` should redirect to next step -- `/select_day` with options to select desired week day (Monday-Friday)
        - button `/book_for_{selected_day}` should be displayed

- When person select the day:
    - should be displayed only available timeslots for that day (ex. __"09:00"__; __"10:00"__ etc.);
    - option `/select_time` should be displayed with buttons with all available timeslots for the selected day;

- When person select time -- should be asked to input his/her name;
- When person input his/her name - record to database should be done;
- After record to database is done:
    - should be displayed the schedule for selected day;

#### Reset database and prepare for next week
