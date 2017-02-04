#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from datetime import datetime
from struct import *
from RF24 import *
from RF24Network import *
import Adafruit_DHT
import csv

millis = lambda: int(round(time.time() * 1000))
octlit = lambda n:int(n, 8)
start_time = time.time()
runtime = lambda: '{0:0.2f}s'.format(time.time()-start_time) 

# Address of our node in Octal format (01, 021, etc)
this_node = octlit("00")
sensor_node = octlit("011")


# set up RF24 interfaces
radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8KHZ)
network = RF24Network(radio)

# make sure we got the right RF24 interface
radio.begin()
while not radio.isPVariant():
    time.sleep(1)
    print("searching RF24-Interface...")
    radio.begin()
    
print("ok")
time.sleep(0.1)

#set up RF24 modules
# wifi range: 2402..2482 MHz)
network.begin(90, this_node)    # channel 90 = 2490 MHz
radio.setDataRate(RF24_250KBPS)
radio.printDetails()

packet_last = None
packet_size = 14
packet_counter = 0
packet_loss = 0

log_lastupdate = 0
ext_temperature=0
ext_raw_temperature=0
ext_humidity=0
int_humidity=0
int_temperature=0

# set up csv logger
logwriter = None
csvfile = open('/home/henry/data.csv', 'ab')
if csvfile:
  logwriter = csv.writer(csvfile, delimiter=' ')

try:
  while 1:
    network.update()
    while network.available():
      header, payload = network.read(packet_size)
#      print(len(payload))
      
      # valid packet received?
      if len(payload) == packet_size:
        
        # extract payload
        ext_temperature, ext_raw_temperature, ext_humidity, number = unpack('<fHfL', bytes(payload))
        

        #update session stats
        packet_counter += 1
        if packet_last:
          packet_loss += (number - packet_last - 1)
        packet_last = number
        
        # show data
        print('Received packet', number, 'at',runtime(),'from node', oct(header.from_node), ' -  Temperature: {0:0.2f}°C'.format(ext_temperature), 'Raw:', ext_raw_temperature,' Humidity: {0:0.0f}%'.format(ext_humidity))

        # save received data
    if (millis() - log_lastupdate) > 10000:
      log_lastupdate = millis()
      int_humidity, int_temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
#      logwriter.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '{0:0.1f}'.format(int_temperature), '{0:0.0f}'.format(int_humidity), '{0:0.1f}'.format(ext_temperature)])
#      csvfile.flush()
        
    time.sleep(0.2)
except KeyboardInterrupt:
  print()
  print('================== Session Stats ==================')
  print('packet_counter:',packet_counter)
  print('packet_loss:',packet_loss, '({0:0.1f}%)'.format(float(packet_loss)/float(packet_loss+packet_counter+0.0001)*100.))
finally:
  print()
  print('finished');
