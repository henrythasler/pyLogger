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

    x = data[0]
    y = data[1]

    print(x.size, x[0])
    print(y.size, y[0])

    y = np.convolve(np.array(data[1], dtype=np.float), np.ones((N,))/N, mode='valid')
    x = x[:y.size]
    print(x.size, x[0])
    print(y.size, y[0])


    fig, ax = plt.subplots()

    ax.set(xlabel='', ylabel='Temperatur [C]', title='Innen- und Aussentemperatur')

    ax.annotate('17.1kHz', xy=(17100, -15), xytext=(1500, -25),
                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )

    ax.annotate('21.7kHz', xy=(21700, -25), xytext=(50000, -25),
                arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
                )

    ax.plot(x, y)
    ax.grid(True, zorder=5)


    plt.show()

except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    if con:
        con.close()