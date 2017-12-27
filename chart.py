#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
from datetime import datetime, timedelta
import numpy as np
import sys
import math
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

ROOTDIR = "/home/henry/pyLogger"

con = None
N = 10

try:
    con = lite.connect(ROOTDIR+'/temperature.db', detect_types=lite.PARSE_DECLTYPES)
    
    cur = con.cursor()
    #cur.execute('SELECT SQLITE_VERSION()')
    #data = cur.fetchone()
    #print "SQLite version: %s" % data                


    cur.execute("SELECT time, temp FROM outside WHERE time >= date('now', '-7 day')")
    con.commit()
    data = np.transpose(np.array(cur.fetchall()))

    outside = {}
    outside["y"] = np.convolve(np.array(data[1], dtype=np.float), np.ones((N,))/N, mode='valid')
    outside["x"] = data[0][N/2:data[0].size-N/2+1]
    outside["maxx"] = np.argmax(outside["y"])
    outside["maxy"] = outside["y"][outside["maxx"]]
    outside["minx"] = np.argmin(outside["y"])
    outside["miny"] = outside["y"][outside["minx"]]

    cur.execute("SELECT time, temp FROM livingroom WHERE time >= date('now', '-7 day')")
    con.commit()
    data = np.transpose(np.array(cur.fetchall()))

    # filter sensor glitches
    limit = 1
    b = np.diff(data[1])
    c = np.where(np.abs(b)>limit)[0]
    for i, d in enumerate(c[::2]):
        val = data[1][d]
        for e in range(d, c[2*i+1]):
            data[1][e+1] = val

    livingroom = {}
    livingroom["y"] = np.convolve(np.array(data[1], dtype=np.float), np.ones((N,))/N, mode='valid')
    livingroom["x"] = data[0][N/2:data[0].size-N/2+1]
    livingroom["maxx"] = np.argmax(livingroom["y"])
    livingroom["maxy"] = livingroom["y"][livingroom["maxx"]]
    livingroom["minx"] = np.argmin(livingroom["y"])
    livingroom["miny"] = livingroom["y"][livingroom["minx"]]
 

    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)

    ax.set_ylabel(u"Temperatur [°C]", fontsize=10)
    ax.set_title(u"Innen- und Außentemperatur", fontsize=20)
    plt.setp(ax.get_xticklabels(), fontsize=10, color="#525252")
    plt.setp(ax.get_yticklabels(), fontsize=10, color="#525252")

    # position bottom right
    fig.text(0.5, 0, datetime.now().strftime("%Y-%m-%d %H:%M"),
         fontsize=8, color='black',
         ha='center', va='bottom', alpha=0.4)

    
    ax.annotate(u"↑{:.1f}°C".format(outside["maxy"]), xy=(outside["x"][outside["maxx"]], outside["maxy"]), 
                xytext=(outside["x"][outside["maxx"]+100], outside["maxy"]),
#                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )
    ax.annotate(u"↓{:.1f}°C".format(outside["miny"]), xy=(outside["x"][outside["minx"]], outside["miny"]), 
                xytext=(outside["x"][outside["minx"]+100], outside["miny"]-.4),
#                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )

    ax.annotate(u"↑{:.1f}°C".format(livingroom["maxy"]), xy=(livingroom["x"][livingroom["maxx"]], livingroom["maxy"]), 
                xytext=(livingroom["x"][livingroom["maxx"]+100], livingroom["maxy"]),
#                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )

    ax.annotate(u"↓{:.1f}°C".format(livingroom["miny"]), xy=(livingroom["x"][livingroom["minx"]], livingroom["miny"]), 
                xytext=(livingroom["x"][livingroom["minx"]+100], livingroom["miny"]-.4),
#                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )

#    ax.plot(outside["x"], outside["y"], color="#005AC8", linewidth=2, marker='o', linestyle='-', markerfacecolor="white", ms=6, markevery=[outside["maxx"]])
    ax.plot_date(outside["x"], outside["y"], xdate=True, color="#005AC8", linewidth=2, marker='', linestyle='-')

#    ax.plot(livingroom["x"], livingroom["y"], color="#FA1400", linewidth=2, linestyle='-', marker='o', markerfacecolor="white", ms=6, markevery=[np.argmax(livingroom["y"])])
    ax.plot_date(livingroom["x"], livingroom["y"], xdate=True, color="#FA1400", linewidth=2, marker='', linestyle='-')

    ax.grid(linewidth=.5, color="#cccccc", zorder=-5)

    # make sure we see whole day intervals
    xmin, xmax = plt.xlim()
    plt.xlim(math.ceil(xmin), math.ceil(xmax))
    
    ax.axhline(linewidth=.5, color="black")
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=[6,18]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%a %Hh'))

    # make sure we maximize the used drawing area
    fig.autofmt_xdate()
    plt.tight_layout()

#    plt.show() # use for interactive view only
    
    fig.savefig(ROOTDIR+'/out.png', dpi=100)     # save as file (800x600)
    plt.close(fig)    # close the figure      

except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    if con:
        con.close()


def on_connect(client, userdata, flags, rc):
    #print("Connected to mqtt broker with result code "+str(rc))
    with open(ROOTDIR+'/out.png') as f:
      img = f.read()
      f.close()
      byteArray = bytearray(img)
      client.publish("home/img/tempchart", byteArray, retain=True)
      
def on_publish(client, userdata, mid):
  # Disconnect after our message has been sent.
  client.disconnect()
 
client = mqtt.Client('chart-%s' % os.getpid())
client.on_connect = on_connect
client.on_publish = on_publish
 
client.connect("127.0.0.1")
client.loop_start()
time.sleep(2)
client.loop_stop()