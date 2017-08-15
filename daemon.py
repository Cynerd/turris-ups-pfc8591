#!/usr/bin/env python

import ubus
import sys
import os
import time
from periphery import I2C
import sqlite3
import commands

# 60mV per step
power_supply_cut_off = 212
power_supply_reaquare = 215
battery_low = 202 
battery_not_low = 206
battery_high = 260
battery_not_high = 250

# TODO use __main__

# Initialize I2C
i2c = I2C("/dev/i2c-7")

# Initialize sqlite
db_connection = sqlite3.connect('/tmp/ups-pfc8591.db')
db = db_connection.cursor()

# Initialize ubus
ubus.connect()

def read_chunk(handler, data):
    result = []
    for row in db.execute('SELECT date, %s FROM collected_data WHERE date > %s' %  \
            (data['field'], (int(time.time()) - data['range']))):
        result.append((row[0], row[1]))
    handler.reply({"data": result})

ubus.add(
    "ups-pfc8591", {
        "read_data": {
            "method": read_chunk,
            "signature": {"range": ubus.BLOBMSG_TYPE_INT32, "field": ubus.BLOBMSG_TYPE_STRING},
        },
    }
)

db.execute('''CREATE TABLE IF NOT EXISTS collected_data (
    date INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    light INTEGER NOT NULL,
    voltage INTEGER NOT NULL,
    trimmer INTEGER NOT NULL
)''')

def i2c_get(addr):
    msg = [I2C.Message([addr]), I2C.Message([0x00], read=True)]
    i2c.transfer(0x48, msg)
    return msg[1].data[0]

def load_data():
    return {
            'trimmer': i2c_get(0x40),
            'temperature': i2c_get(0x41),
            'light': i2c_get(0x42),
            'voltage': i2c_get(0x43)
        }

def db_data(data):
    db.execute('''INSERT INTO collected_data (date, temperature, light, voltage, trimmer) VALUES
            (%s, %s, %s, %s, %s)''' % (str(int(time.time())), data['temperature'], data['light'], data['voltage'], data['trimmer']))
    db_connection.commit()

def ubus_data(data):
    date = str(int(time.time()))
    for k in iter(data.keys()):
        ubus.send("ups-pfc8591", {k: (date, data[k])})

notified_power_supply = False
notified_low_battery = False
notified_high_battery = False

def check_data(data):
    global notified_low_battery, notified_power_supply, notified_high_battery
    for k in data:
        if k == "voltage":
            if data['voltage'] > power_supply_reaquare and notified_power_supply:
                commands.getoutput('create_notification -s news "Sitove napajeni bylo obnoveno." "Power supply was reaquired."')
                notified_power_supply = False
            elif data['voltage'] <= power_supply_cut_off and not notified_power_supply: # 12.8V
                commands.getoutput('create_notification -s error "Vypadlo sitove napajeni!" "Power supply was interrupted!"')
                notified_power_supply = True
            if data['voltage'] > battery_not_low and notified_low_battery:
                notified_low_battery = False
            elif data['voltage'] <= battery_low and not notified_low_battery: # 12V
                volts = float(data['voltage']) * 0.0593
                commands.getoutput('create_notification -s error "Nizke napetu akumulatoru! %.2f V" "Low voltage of the acumulator! %.2f V"' % (volts, volts))
                notified_low_battery = True
            if data['voltage'] <= battery_not_high and notified_high_battery:
                notified_high_battery = False
            elif data['voltage'] > battery_high and not notified_high_battery:
                commands.getoutput('create_notification -s error "Vysoke napetu akumulatoru!" "High voltage of the acumulator!"')
                notified_high_battery = True

# TODO add to exit handler
# i2c.close()

while True:
    ubus.loop(60000)
    data = load_data()
    #print(data)
    db_data(data)
    ubus_data(data)
    check_data(data)
