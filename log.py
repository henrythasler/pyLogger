#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from datetime import datetime
from struct import *
#import adafruit_dht
import board
import csv
import paho.mqtt.client as mqtt
import json
import sqlite3 as lite


# sudo apt install postgresql-client libpq-dev
# sudo pip install psycopg2
import psycopg2 as pg

ROOTDIR = "/home/henry/pyLogger"

millis = lambda: int(round(time.time() * 1000))
octlit = lambda n:int(n, 8)
start_time = time.time()
runtime = lambda: '{0:0.2f}s'.format(time.time()-start_time) 

log_lastupdate = millis()-60001
ext_temperature = None
int_humidity={
    'value': None,
    'timestamp': None,
    'unit': '%'
    }
int_temperature={
    'value': None,
    'timestamp': None,
    'unit': '°C'
    }

# set up csv logger
#logwriter = None
#csvfile = open('/home/henry/pyLogger/data.csv', 'ab')
#if csvfile:
#  logwriter = csv.writer(csvfile, delimiter=';')

con = None
cur = None
try:
    con = lite.connect(ROOTDIR+'/temperature.db', detect_types=lite.PARSE_DECLTYPES)
    cur = con.cursor()
except lite.Error as e:
    print("Error {}:".format(e.args[0]))
    sys.exit(1)

pg_con = None
pg_cur = None   
try:
    pg_con = pg.connect("dbname='home' user='postgres' host='omv4.fritz.box' password='postgres'")
    pg_cur = pg_con.cursor()
except Exception as e:
    print("Postgres Error {}:".format(e))

        
#setup mqtt stuff
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/out/temp")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global ext_temperature
    
#    print(msg.topic+" "+msg.payload)
    ext_temperature = json.loads(msg.payload)
    ext_temperature["timestamp"] = int(ext_temperature["timestamp"])
   
    #print(" "+str(ext_temperature))
    

client = mqtt.Client("pyLogger")
client.on_connect = on_connect
client.on_message = on_message

client.connect("omv4.fritz.box")
client.loop_start()

#dhtDevice = adafruit_dht.DHT22(board.D4)

try:
    while 1:
          # save received data
        if (millis() - log_lastupdate) > 60000:
            log_lastupdate = millis()
#            try:
                #int_temperature["value"] = dhtDevice.temperature
                #int_humidity["value"] = dhtDevice.humidity
#            except:
#                pass
#            int_humidity["value"] = int(int_humidity["value"] - 0)    # offset correction
#            int_temperature["value"] = round(int_temperature["value"], 1)
#            int_temperature["timestamp"] = int(time.time())
#            int_humidity["timestamp"] = int(time.time())
            
#            client.publish("home/in/temp", json.dumps(int_temperature), retain=True)
#            client.publish("home/in/temp/value", '{0:0.1f}'.format(int_temperature["value"]), retain=True)
#            client.publish("home/in/hum", json.dumps(int_humidity), retain=True)
#            client.publish("home/in/hum/value", int_humidity["value"], retain=True)

#           cur.execute("INSERT INTO livingroom(time, temp, hum) VALUES(?, ?, ?)", (datetime.now(), int_temperature["value"], int_humidity["value"]))
#            pg_cur.execute("INSERT INTO livingroom(timestamp, temperature, humidity) VALUES(%s, %s, %s)", (datetime.utcnow(), int_temperature["value"], int_humidity["value"]))
            
            if (ext_temperature == None) or (( (millis()/1000 - ext_temperature["timestamp"]) > 600) and (ext_temperature["timestamp"] > 0)) :
                pass
            else:
                cur.execute("INSERT INTO outside(time, temp, hum) VALUES(?, ?, ?)", (datetime.now(), ext_temperature["value"], None))
                pg_cur.execute("INSERT INTO outside(timestamp, temperature, humidity) VALUES(%s, %s, %s)", (datetime.utcnow(), ext_temperature["value"], None))
            con.commit()
            pg_con.commit()

                
#            if (ext_temperature == None) or (( (millis()/1000 - ext_temperature["timestamp"]) > 600) and (ext_temperature["timestamp"] > 0)) :
#              logwriter.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '{0:0.1f}'.format(int_temperature["value"]), '{0:0.0f}'.format(int_humidity["value"]), '-'])
#            else:
#              logwriter.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '{0:0.1f}'.format(int_temperature["value"]), '{0:0.0f}'.format(int_humidity["value"]), '{0:0.1f}'.format(ext_temperature["value"])])

#            csvfile.flush()
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    if con:
        con.close()            
