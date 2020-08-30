sender_email = 'from@gmail.com'
password = 'my_password' #gmail password, make sure unsecure 3rd party enabled
filename = 'air_colors.json' #you can leave this as is

user_confs = {}

user_confs['user1'] = {
	'to_emails': ['to@gmail.com'],
	#some number, mine is 5-digits long
	#find at https://www.purpleair.com/json
	'sensor_id': 10842,
	#These don't necessarily need to be changed
	#an int, which sets the minimum 'severity' for which to notify. e.g. `3` is orange
	'min_color_notif_threshold': 3,
	#sets max severity for which to nofity.
	'max_color_notif_threshold': None,
	#which counter you'd like to use readings from.
	#If not set to `a` or `b`, uses the average of both.
	'counter': None,
	'conversion_method': None, #only supported is 'lrapa'
	}
