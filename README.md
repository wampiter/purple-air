# purple-air
Script to monitor a [PurpleAir](https://www.purpleair.com/) station, and notify on PM2.5 changes. The script monitors a single PurpleAir station, and sends an email via gmail when the PM2.5 crosses a 'color' threshold.

You can find PurpleAir's API documentation [here](https://docs.google.com/document/d/15ijz94dXJ-YAZLi9iZ_RaBwrZ4KtYeCy08goGBwnbCU/edit).

## Setup:

0. python3 is required.

1. Copy sample_config.py to config.py and set relevant params there. Important params to set:
* `sensor_id`
* `sender_email`
* `to_emails`
* `password`

2. run code as cron job:
* open your cron table: `crontab -e`
* make a row that runs this every e.g. 10 minutes: `*/10 * * * * python3 /path/to/purple-air/purple_air.py`

TO DO:
* add hysteresis (e.g. don't e-mail me unless change persists for 2 checks, and/or don't e-mail me if already e-mailed me in the last few checks.)
