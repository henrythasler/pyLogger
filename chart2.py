#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

con = None
N = 10

try:
    con = lite.connect('temperature.db', detect_types=lite.PARSE_DECLTYPES)
    
    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    print "SQLite version: %s" % data                


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
    fig.set_size_inches(10, 7.5)

    ax.set_ylabel(u"Temperatur [°C]", fontsize=12)
    ax.set_title(u"Innen- und Außentemperatur", fontsize=20)

    # position bottom right
    fig.text(0.5, 0, "Chart generated on " + datetime.now().strftime("%Y-%m-%d %H:%M"),
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
    ax.plot(outside["x"], outside["y"], color="#005AC8", linewidth=2)

#    ax.plot(livingroom["x"], livingroom["y"], color="#FA1400", linewidth=2, linestyle='-', marker='o', markerfacecolor="white", ms=6, markevery=[np.argmax(livingroom["y"])])
    ax.plot(livingroom["x"], livingroom["y"], color="#FA1400", linewidth=2)

    ax.grid(True, zorder=5)

    plt.tight_layout()
    plt.show()

except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    if con:
        con.close()