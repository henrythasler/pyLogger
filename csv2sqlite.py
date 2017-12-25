#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from datetime import datetime, timedelta


con = None

try:
    con = lite.connect('temperature.db', detect_types=lite.PARSE_DECLTYPES)
    
    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    print "SQLite version: %s" % data                

    cur.execute("DROP TABLE IF EXISTS outside")
    cur.execute("DROP TABLE IF EXISTS livingroom")
    cur.execute("CREATE TABLE outside(time timestamp, temp REAL, hum INT)")
    cur.execute("CREATE TABLE livingroom(time timestamp, temp REAL, hum INT)")

    with open("data.csv", "r") as csvfile:
        for line in csvfile:
            row = line.rstrip().split(";")
            try:
                csv_temperature = float(row[1])
                csv_humidity = float(row[2])
                if row[3] == '-':
                    csv_ext_temperature = None
                else:
                    csv_ext_temperature = float(row[3])
                csv_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                cur.execute("INSERT INTO outside(time, temp, hum) VALUES(?, ?, ?)", (csv_time, csv_ext_temperature, None))
                cur.execute("INSERT INTO livingroom(time, temp, hum) VALUES(?, ?, ?)", (csv_time, csv_temperature, int(csv_humidity)))
            except:
                print("CSV Error:", row)
        con.commit()

except lite.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    if con:
        con.close()
        print("all done")
