# pyLogger
log sensor data

#crontab entry to generate
0,30 * * * * /home/henry/pyLogger/chart.py > /dev/null 2>&1
