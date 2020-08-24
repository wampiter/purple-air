import smtplib, ssl
from datetime import datetime
from urllib.request import Request, urlopen
import json
from enum import Enum
import os

import config

PURPLE_AIR_URL_PREFIX = 'https://www.purpleair.com/json?show='
smtp_server = "smtp.gmail.com"
port = 587  # For starttls

SENSOR_ID = config.sensor_id
FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/' + config.filename
MIN_COLOR_NOTIF_THRESHOLD = config.min_color_notif_threshold
MAX_COLOR_NOTIF_THRESHOLD = config.max_color_notif_threshold
COUNTER_STRATEGY = config.counter # 'a' -> Counter 0, 'b' -> Counter 1, 'both' -> average of both
CONVERSION_METHOD = config.conversion_method
SENDER_EMAIL = config.sender_email
TO_EMAILS = config.to_emails
PASSWORD = config.password

context = ssl.create_default_context()

def send_gmail(sender_email, to_emails, password, message):
	'''log onto server and send message from sender_email to to_emails'''
	try:
	    server = smtplib.SMTP(smtp_server,port)
	    server.starttls(context=context) # Secure the connection
	    server.login(sender_email, password)
	    for to_email in to_emails:
	        server.sendmail(sender_email, to_email, message)
	except Exception as e:
	    print('errin yo')
	    print(e)
	finally:
	    server.quit()

class Color(Enum):
    green        = 1
    yellow       = 2
    orange       = 3
    red          = 4
    purple       = 5
    maroon       = 6
    hella_maroon = 7


# Source: https://aqicn.org/faq/2013-09-09/revised-pm25-aqi-breakpoints/
def current_color(pm_2_5_value):
    if pm_2_5_value <= 12.0:
        return Color.green
    elif pm_2_5_value <= 35.4:
        return Color.yellow
    elif pm_2_5_value <= 55.4:
        return Color.orange
    elif pm_2_5_value <= 150.4:
        return Color.red
    elif pm_2_5_value <= 250.4:
        return Color.purple
    elif pm_2_5_value <= 350.4:
        return Color.maroon
    else:
        return Color.hella_maroon #shit


def get_sensor_data():
    print("Attempting to open "+ PURPLE_AIR_URL_PREFIX + str(SENSOR_ID))
    return json.load(urlopen(PURPLE_AIR_URL_PREFIX + str(SENSOR_ID)))


def pm_2_5_average(data):
    stats0 = json.loads(data["results"][0]["Stats"])
    stats1 = json.loads(data["results"][1]["Stats"])

    if COUNTER_STRATEGY == "a":
        reading = rstats0["v"]
    elif COUNTER_STRATEGY == "b":
        reading = stats1["v"]
    else:
        reading = (stats0["v"] + stats1["v"])/2.

    # we only consider the lrapa conversion for now, though there are others.
    if CONVERSION_METHOD == 'lrapa':
        return reading * 0.5 - 0.66 # see https://www.lrapa.org/DocumentCenter/View/4147/PurpleAir-Correction-Summary
    else:
        return reading

def get_last_color():
    try:
        with open(FILENAME, 'r') as f:
            color_name = f.read().strip()
    except FileNotFoundError:
        print('No previous color. Pretending it was green.')
        color_name = 'green'
    return Color[color_name]

def update_color(color):
    with open(FILENAME, 'w') as f:
        f.write(color.name)

def notify_color_change(old_color, new_color):
    if old_color.value < new_color.value:
        print("degraded")
        message = "The air has degraded from " + old_color.name + " to " + new_color.name
    else:
        print("improved")
        message = "The air has improved from " + old_color.name + " to " + new_color.name
    print("About to send notification of change")
    send_gmail(SENDER_EMAIL, TO_EMAILS, PASSWORD, message)


def should_notify_color_change(old_color, new_color):
    if MIN_COLOR_NOTIF_THRESHOLD is not None:
        big_enough = max(old_color.value, new_color.value) >= MIN_COLOR_NOTIF_THRESHOLD
    else:
        big_enough = True
    if MAX_COLOR_NOTIF_THRESHOLD is not None:
        small_enough = min(old_color.value, new_color.value) <= MAX_COLOR_NOTIF_THRESHOLD
    else:
        small_enough = True
    return (big_enough and small_enough)

def main():
    print('Checking on sensor {} at {}...'.format(SENSOR_ID, datetime.now()))
    try:
        current_data = get_sensor_data()
        current_pm_2_5 = pm_2_5_average(current_data)

        print("current pm2.5 reading is: " +  str(current_pm_2_5))

        new_color = current_color(current_pm_2_5)
        last_color = get_last_color()

        if not new_color == last_color:
            print("new color!")
            update_color(new_color)
            if should_notify_color_change(last_color, new_color):
                print("sending color change notification")
                notify_color_change(last_color, new_color)
            else:
                print("change outside notification thresholds")
        else:
            print("no change in color (still " + new_color.name + ")")
    except:
        print('Check failed!')
        raise
    else:
        print('Check succeeded!')
        return datetime.now()
    finally:
        print('Check complete at {}'.format(str(datetime.now())))

if __name__ == '__main__':
	main()
