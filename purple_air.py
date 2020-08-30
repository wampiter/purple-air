import smtplib, ssl
from datetime import datetime
from urllib.request import Request, urlopen
import json
from enum import Enum
import os
from time import sleep

import config

PURPLE_AIR_URL_PREFIX = 'https://www.purpleair.com/json?show='
smtp_server = "smtp.gmail.com"
port = 587  # For starttls

USER_CONFS = config.user_confs
FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/' + config.filename
SENDER_EMAIL = config.sender_email
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


def get_sensor_data(user_conf):
    print("Attempting to open "+ PURPLE_AIR_URL_PREFIX + str(user_conf['sensor_id']))
    return json.load(urlopen(PURPLE_AIR_URL_PREFIX + str(user_conf['sensor_id'])))


def pm_2_5_average(user_conf, data):
    stats0 = json.loads(data["results"][0]["Stats"])
    stats1 = json.loads(data["results"][1]["Stats"])

    if user_conf['counter'] == "a":
        reading = rstats0["v"]
    elif user_conf['counter'] == "b":
        reading = stats1["v"]
    else:
        reading = (stats0["v"] + stats1["v"])/2.

    # we only consider the lrapa conversion for now, though there are others.
    if user_conf['conversion_method'] == 'lrapa':
        return reading * 0.5 - 0.66 # see https://www.lrapa.org/DocumentCenter/View/4147/PurpleAir-Correction-Summary
    else:
        return reading

def notify_color_change(user_conf, old_color, new_color):
    if old_color.value < new_color.value:
        print("degraded")
        message = "The air has degraded from " + old_color.name + " to " + new_color.name
    else:
        print("improved")
        message = "The air has improved from " + old_color.name + " to " + new_color.name
    print("About to send notification of change")
    send_gmail(SENDER_EMAIL, user_conf['to_emails'], PASSWORD, message)


def should_notify_color_change(user_conf, old_color, new_color):
    if user_conf['min_color_notif_threshold'] is not None:
        big_enough = max(old_color.value, new_color.value) >= user_conf['min_color_notif_threshold']
    else:
        big_enough = True
    if user_conf['max_color_notif_threshold'] is not None:
        small_enough = min(old_color.value, new_color.value) <= user_conf['max_color_notif_threshold']
    else:
        small_enough = True
    return (big_enough and small_enough)

def do_user(user_conf):
    '''Do everythign for a user'''
    print('Checking on sensor {} at {}...'.format(user_conf['sensor_id'], datetime.now()))
    try:
        current_data = get_sensor_data(user_conf)
        current_pm_2_5 = pm_2_5_average(user_conf, current_data)
        new_color = current_color(current_pm_2_5)
        last_color = user_conf.get('last_color')
        if (last_color is not None) and (new_color != Color[last_color]) :
            print("new color!")
            last_color = Color[last_color]
            if should_notify_color_change(user_conf, last_color, new_color):
                print("sending color change notification")
                notify_color_change(user_conf, last_color, new_color)
            else:
                print("change outside notification thresholds")
        else:
            print("no change in color (still " + new_color.name + ")")
    except Exception as e:
        print('Check failed for ' + str(user_conf['user']))
        # send_gmail(SENDER_EMAIL, user_conf['to_emails'], PASSWORD, str(e))
        print(e)
        return user_conf['last_color']
    else:
        print('Check succeeded!')
        return new_color.name
    finally:
        print('Check complete at {}'.format(str(datetime.now())))

def main():
    #Load file of prev colors
    try:
        with open(FILENAME, 'r') as f:
            last_colors = json.loads(f.read())
    except FileNotFoundError:
        last_colors = {} #empty dict equivalent to no users
    for user, color in last_colors.items():
        USER_CONFS[user]['last_color'] = color

    new_colors = {} #dict to store colors for each user
    for user, user_conf in USER_CONFS.items():
        user_conf['user'] = user
        new_color = do_user(user_conf)
        new_colors[user] = new_color
        sleep(1) #avoid overloading URL

    with open(FILENAME, 'w') as f:
        f.write(json.dumps(new_colors))

if __name__ == '__main__':
	main()
