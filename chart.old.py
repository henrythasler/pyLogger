#!/usr/bin/env python
# -*- coding: utf-8 -*-

# called by cron-job

import os
import time

import plotly.offline as py
import plotly.graph_objs as go

import numpy as np

from datetime import datetime, timedelta
from subprocess import call

import paho.mqtt.client as mqtt
import struct

def to_unix_time(dt):
    epoch =  datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

ROOTDIR = "/home/henry/pyLogger"

#PHANTOMJS = ROOTDIR+"/phantomjs-2.1.1/phantomjs-2.1.1-linux-armhf"
PHANTOMJS = ROOTDIR+"/phantomjs-armv7/bin/phantomjs"



N = 10

x = []
y1 = []
y2 = []
y3 = []

y1_avg = []
y2_avg = []


with open(ROOTDIR+'/data.csv', "rb") as csvfile:
  last_temperature = 0;
  last_humidity = 0;
  timeframe = datetime.now() - timedelta(days=7)
  timeframe = timeframe.replace(second=0, microsecond=0,minute=0,hour=0)
  
  csvfile.seek(-60*24*8*34, os.SEEK_END)
  next(csvfile)
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
      
      if csv_time >= timeframe:
        x.append(csv_time)
        y3.append(csv_ext_temperature)   
                
        if len(y1)>0:
          if (abs(csv_temperature - last_temperature) < 1.0):            
            y1.append(csv_temperature)
            last_temperature = csv_temperature
          else:
#            print('skipped', csv_temperature)
            y1.append(last_temperature)
#            last_temperature = csv_temperature
        else:
          y1.append(csv_temperature)
          last_temperature = csv_temperature


        if len(y2)>0:
          if (abs(csv_humidity - last_humidity) < 5):
            y2.append(csv_humidity)
            last_humidity = csv_humidity
          else:
            y2.append(last_humidity)
        else:
          y2.append(csv_humidity)
          last_humidity = csv_humidity
          
    except:
      pass
    
traces = []

traces.append(go.Scatter(
        x=x,
#        y=y1,
        y=np.convolve(np.array(y1, dtype=np.float), np.ones((N,))/N, mode='valid'),
#        mode = 'lines+markers',
        mode = 'lines',
        marker = dict(
          maxdisplayed= 100
          ),
        line = dict(
          color = ('rgb(250, 20, 0)'),
          width = 3,
        ),
        name = 'Innen',
    ))

traces.append(go.Scatter(
        x=x,
#	y=y3,
        y=np.convolve(np.array(y3, dtype=np.float), np.ones((N,))/N, mode='valid'),
#        mode = 'lines+markers',
        mode = 'lines',
        marker = dict(
          maxdisplayed= 100
          ),
        line = dict(
          color = ('rgb(0, 90, 200)'),
          width = 3,
        ),
        name = 'Außen',
    ))

'''        
traces.append(go.Scatter(
        x=x,
#        y=y2,
        y=np.convolve(y2, np.ones((N,))/N, mode='valid'),
        yaxis="y2",
#        mode = 'lines+markers',
        mode = 'lines',
        marker = dict(
          maxdisplayed= 100
          ),
        line = dict(
          color = ('rgb(16, 196, 0)'),
          width = 3,
        ),
        name = 'Luftfeuchtigkeit',
    ))
'''
    
layout = go.Layout(
    autosize=False,
    width=800,
    height=600,
    margin=dict(
        l=50,
        r=30,
        b=80,
        t=50,
        pad=0
    ),
  
    # https://plot.ly/javascript-graphing-library/reference/#xaxis
    xaxis=dict(
        showline=True,
#        showgrid=False,
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        autotick=False,
#        nticks=4,
        range=[to_unix_time(timeframe), to_unix_time(timeframe + timedelta(days=8))],
        tick0 = to_unix_time(timeframe.replace(second=0, microsecond=0,minute=0,hour=4)),
        dtick=3600000*12,
        tickcolor='rgb(204, 204, 204)',
        tickwidth=2,
        ticklen=5,
        # https://github.com/d3/d3/wiki/Time-Formatting
        tickformat='%a, %Hh',
        tickfont=dict(
#            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),  
    yaxis=dict(
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        title=u'Temperatur [°C]',
        showticklabels=True,
        ticks='outside',
        tickcolor='rgb(204, 204, 204)',
        tickwidth=2,
        ticklen=5,
        tickfont=dict(
#            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    showlegend=False,
)
'''        
    yaxis2=dict(
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        showgrid=False,
        title='Luftfeuchtigkeit [%]',
        overlaying='y',
        side='right',
        showticklabels=True,
        ticks='outside',
        tickcolor='rgb(204, 204, 204)',
        tickwidth=2,
        ticklen=5,
        tickfont=dict(
#            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    )
)
'''

annotations = []

# Title
annotations.append(dict(xref='paper', yref='paper', x=0.5, y=1.025,
                              xanchor='center', yanchor='bottom',
                              text='Innen- und Außentemperatur',
                              font=dict(
#                                        family='Arial',
                                        size=30,
                                        color='rgb(37,37,37)'),
                              showarrow=False,))
# Source
annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.12,
                              xanchor='center', yanchor='top',
                              text='Chart generated on ' + datetime.now().strftime("%Y-%m-%d %H:%M"),
                              font=dict(
#                                        family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False,))

layout['annotations'] = annotations
    
fig = go.Figure(data=traces, layout=layout)


#py.init_notebook_mode()
#py.iplot({'data': [{'y': [4, 2, 3, 4]}], 'layout': {'title': 'Test Plot'}}, image='png')

#py.plot(fig, auto_open=False, image = 'png', image_filename='out.png', output_type='file', image_width=800, image_height=600, filename='temp-chart.html', validate=False)

py.plot(fig, filename=ROOTDIR+'/temp-chart.html', auto_open=False, show_link=False)
call([PHANTOMJS,ROOTDIR+"/capture.js", "file:///"+ROOTDIR+"/temp-chart.html"]) 


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
