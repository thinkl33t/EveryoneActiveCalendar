import requests
from icalendar import Calendar, Event, Timezone
import datetime
import pytz
import uuid

conf = {
    'center': '0201',
    'filters': {
        # 'categories': [
        #   'Swimming Timetables',
        # ],
        # 'whats': [
        #   'Family & Fun',
        #   'Fitness & Health',
        # ],
        # 'locations': [
        #   'Main Pool',
        # ],
        'descriptions': [
          'Swim 4 Everyone - Main Pool',
          'Swim 4 Fitness - Main Pool',
        ]
    },
}

days_of_week = {
    'Monday':   0,
    'Tuesday':  1,
    'Wednesday':2,
    'Thursday': 3,
    'Friday':   4,
    'Saturday': 5,
    'Sunday':   6,
}

with requests.get('https://api.everyoneactive.com/v1.0/centres/{center}/timetable'.format(**conf)) as r:
    filtered_by_category = [i for i in r.json()['items'] if 'categories' not in conf['filters'] or i['category'] in conf['filters']['categories'] or len(conf['filters']['categories']) == 0]
    filtered_by_what = [i for i in filtered_by_category if 'whats' not in conf['filters'] or i['what'] in conf['filters']['whats'] or len(conf['filters']['whats']) == 0]
    filtered_by_location = [i for i in filtered_by_what if 'locations' not in conf['filters'] or i['location'] in conf['filters']['locations'] or len(conf['filters']['locations']) == 0]
    filtered_by_description = [i for i in filtered_by_location if 'descriptions' not in conf['filters'] or i['description'] in conf['filters']['descriptions'] or len(conf['filters']['descriptions']) == 0]

    cal = Calendar()
    cal.add('timezone_id', 'Europe/London')
    cal.add('name', 'Everyone Active Calender - Center {center}'.format(**conf))
    cal.add('prodid', '-//create-ical.py//EveryoneActiveCalendar//'.format(**conf))
    cal.add('version', '2.0')

    week_start_date = datetime.date.today() + datetime.timedelta(days=-datetime.date.today().weekday())

    for i in filtered_by_description:
        for day in i['times']:
            day_start_date = week_start_date + datetime.timedelta(days=days_of_week[day])

            for time in i['times'][day]:

                start_time = datetime.time(
                                hour=int(time['start'].split(':',1)[0]),
                                minute=int(time['start'].split(':',1)[1]),
                                tzinfo=pytz.timezone("Europe/London")
                                )

                end_time = datetime.time(
                                hour=int(time['end'].split(':',1)[0]),
                                minute=int(time['end'].split(':',1)[1]),
                                tzinfo=pytz.timezone("Europe/London")
                                )

                new_event = Event()
                new_event.add('summary', time['description'])
                new_event.add('description', i['full_description'])
                new_event.add('location', i['location'])
                new_event.add('dtstart', datetime.datetime.combine(day_start_date, start_time).astimezone(pytz.utc))
                new_event.add('dtend', datetime.datetime.combine(day_start_date, end_time).astimezone(pytz.utc))
                new_event.add('dtstamp', datetime.datetime.now())
                new_event.add('uid', uuid.uuid1())

                cal.add_component(new_event)

    print(cal.to_ical().decode("utf-8"))
