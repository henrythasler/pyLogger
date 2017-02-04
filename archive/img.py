#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import struct
import paho.mqtt.client as mqtt
import json
import binascii

ROOTDIR = "/home/henry/pyLogger"

def on_publish(client, userdata, mid):
  # Disconnect after our message has been sent.
  client.disconnect()

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker with result code "+str(rc))
    with open(ROOTDIR+'/out.png') as f:
      img = f.read()
      f.close()
      byteArray = bytearray(img)
      client.publish("home/img/tempchart", byteArray)

client = mqtt.Client('mqtt-test-%s' % os.getpid())
client.on_connect = on_connect
client.on_publish = on_publish

client.connect("127.0.0.1")
client.loop_forever()
