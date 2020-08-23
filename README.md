# purple-air
Script to monitor a [PurpleAir](https://www.purpleair.com/) station, and notify on PM2.5 changes. The script monitors a single PurpleAir station, and sends a notification via gmail when the PM2.5 crosses a 'color' threshold.

For myself, I run it on a cron: every 30 minutes during the day.

You can find PurpleAir's API documentation [here](https://docs.google.com/document/d/15ijz94dXJ-YAZLi9iZ_RaBwrZ4KtYeCy08goGBwnbCU/edit).

Copy sample_config.py to config.py and set relevant params there:
* `min_color_notif_threshold`: an int, which sets the minimum 'severity' for which to notify. I use `3` (which corresponds to 'orange') for myself.
* `sensor_id`: the sensor that you want to monitor. You can find the id for every sensor on PurpleAir [here](https://www.purpleair.com/json).
* `counter`: which counter you'd like to use readings from. If not set to `a` or `b`, the default is to use the average of both. You probably only want to set this to `a` or `b` if you know that one of your counters is not working properly for some reason.
* etc.
