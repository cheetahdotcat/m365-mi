#!/bin/python3

#     Mi365 Scooter Library
#     MiAuth - Authenticate and interact with Xiaomi devices over BLE
#     Copyright (C) 2021  Daljeet Nandha + modified by @catSIXe
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import sys
import json
import os
import argparse
import time
from bluepy import btle

from mim365mi.m365scooter import M365Scooter

#from message import *

import struct

parser = argparse.ArgumentParser()
parser.add_argument("mac", help="mac address of target device")
parser.add_argument("-c", "--command", help="send command (w/o checksum) to uart and print reply")
parser.add_argument("-s", "--serial", action='store_true', help="retrieve serial number")
parser.add_argument("-v", "--version", action='store_true', help="retrieve firmware version")
parser.add_argument("-d", "--debug", action='store_true', help="activate debug log")

parser.add_argument("-r", "--register", action='store_true',
                    help="register with device / create token (caution: will lose bond to all other apps)")
parser.add_argument("-t", "--token_file", default="./mi_token",
                    help="path to mi token file (default: ./mi_token)")

args = parser.parse_args()


from miauth.mi.micrypto import MiCrypto

from paho.mqtt import client as mqtt_client
port = 1883
broker = '127.0.0.1'
username='scooter'
password='PASSWORD'
topic = "m365/test/"
client_id = f'john-xina'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def main():
    mqtt = connect_mqtt()
    mc = M365Scooter(btle.Peripheral(), args.mac, debug=args.debug)

    def lol(reg, payload):
        payloadO = payload
        payload = int.from_bytes(payload, signed=True,  byteorder='little')
        
        if reg == '23010d': #Motor phase A current
            reg = 'esc_phase_a_current'
        if reg == '23010e': #Motor phase B current
            reg = 'esc_phase_b_current'
        if reg == '23010f': #Motor phase C current
            reg = 'esc_phase_c_current'
        if reg == '230175': #drive mode
            reg = 'drive_mode'
        if reg == '230122': #batt percent
            reg = 'bms_level'
        if reg == '230150': #current
            reg = 'esc_current_ma'
            payload = payload * 10
        if reg == '230148': #bms volt
            reg = 'bms_volt'
            payload = payload/1e2
        if reg == '230147': #esc volt
            reg = 'esc_volt'
            payload = payload/1e2
        if reg == '230126': #speed
            reg = 'speed'

        if reg == '230129': #Total mileage, m
            reg = 'total_km'
            payload = payload/1e3
        if reg == '23012F': #Current mileage
            reg = 'current_m'
        if reg == '230132': #Total run time
            reg = 'total_uptime'
        if reg == '23013a': #triptime
            reg = 'triptime1'

        if reg == '23013e': #frame_temp
            reg = 'frame_temp1'
            payload = payload/1e1
        if reg == '2301bb': #frame_temp
            reg = 'frame_temp2'
            payload = payload/1e1
        if reg == '250140': # cell voltages
            reg = 'bms_cell_voltages'
            payload = []
            for i in range(0, 10):
                payload.append(int.from_bytes(payloadO[ (i*2) : (i*2)+2 ], signed=True,  byteorder='little') /1e3)
            payload = json.dumps(payload)
        if reg == '25013b': # battery health
            reg = 'bms_health'
        if reg == '250130': # battery status
            reg = 'bms_status'

        if reg == '25011c': # Charge count
            reg = 'bms_chargecount'
        if reg == '25011b': # Charge full cycles
            reg = 'bms_chargefullcount'
        if reg == '250110': # Serial number
            reg = 'bms_serial'
            payload = payloadO.decode()
        if reg == '250133': # bms current x10mA
            reg = 'bms_current_ma'
            payload = payload * 10
        if reg == '250135': # bms temps high and low bytes, -20C offset
            reg = 'bms_temp1'
            payload = payloadO[ 1 ] - 20
            mqtt.publish(topic + reg, payload)

            reg = 'bms_temp2'
            payload = payloadO[ 0 ] - 20
        print(reg, payload)
        mqtt.publish(topic + reg, payload)
    mc.handleData(lol)

    print("Connecting")
    mc.connect()

    if args.register:
        print("Registering")
        mc.register()
        mc.save_token(args.token_file)
        print("Saved token to:", args.token_file)

    if not mc.token:
        if not os.path.isfile(args.token_file):
            sys.exit("""No authentication token found, register with '-r' or specify path to token file with '-t <path>'.Caution: After registration this device will lose coupling to all other apps (remove/add device in Mi Home app if needed).                     """)

        print("Loading token from:", args.token_file)
        mc.load_token(args.token_file)

    print("Logging in...")
    mc.login()

    '''
    print("Retrieving serial number")

    mc.comm_simplex("55aa032001 10 0e")
    #print("Serial number:", resp.decode())
    time.sleep(3)

    #print("Retrieving firmware version")
    #resp = mc.comm("55aa032001 1a 10")
    #print("Firmware version:", f"{resp[0]}.{resp[1]}")

    cmd = str(battery_info._raw_bytes.hex())
    print("Sending command:", cmd)
    def scooterPowerManagement(reboot=False):
        mc.comm_simplex(Message()                        \
            .set_direction(0x20)                        \
            .set_read_write(ReadWrite.WRITE)            \
            .set_attribute(0x78 if reboot else 0x79)    \
            .set_payload(b'\x01\x00')                   \
        .build()._raw_bytes.hex())
    '''
    
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == topic +'cmds/poweroff':
            scooterPowerManagement(True)
        if msg.topic == topic +'cmds/reboot':
            scooterPowerManagement(True)

    mqtt.subscribe(topic+'cmds/#')
    mqtt.on_message = on_message
    mqtt.loop_start()
    i = 0
    while True:
        i+=1
        # ESC
        if i % 10 == 0:
            mc.comm_simplex('55AA 03 20 01 29 04') # Total mileage, m
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 20 01 2F 02') # Current mileage
            time.sleep(0.05)

            mc.comm_simplex('55AA 03 20 01 32 04') # Total run time
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 20 01 34 04') # ? some run time
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 20 01 3A 04') # ? trip time
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 20 01 3B 04') # ? trip time
            time.sleep(0.05)

        mc.comm_simplex('55AA 03 20 01 22 02') # BMS Percent
        time.sleep(0.05)
        mc.comm_simplex('55AA 03 20 01 26 02') # Speed
        time.sleep(0.05)
        mc.comm_simplex('55AA 03 20 01 47 02') # ESC supply voltage (measured by ESC)
        time.sleep(0.05)
        mc.comm_simplex('55AA 03 20 01 48 02') # Battery voltage (from BMS)
        time.sleep(0.05)
        mc.comm_simplex('55AA 03 20 01 50 02') # Battery current (from BMS)
        time.sleep(0.05)
        if i % 10 == 0:
            mc.comm_simplex('55AA 03 20 01 75 02')
            time.sleep(0.05)
        #       ESC Temperatures
        if i % 10 == 0:
            mc.comm_simplex('55AA 03 20 01 BB 02') #Frame temperature
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 20 01 3E 02') # Frame temperature
            time.sleep(0.05)
    
        # BMS
        if i % 10 == 0:
            mc.comm_simplex('55AA 03 22 01 40 14') # Cell Voltage 1 - 10
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 35 02') # bTemperature1:bTemperature2, Deg C, 0 is -20
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 30 02') # Status
            time.sleep(0.05)
        mc.comm_simplex('55AA 03 22 01 33 02') #Current, x10mA, positive - discharging, negative - charging
        time.sleep(0.05)
        if i % 180 == 0:
            mc.comm_simplex('55AA 03 22 01 10 0E') #Serial number
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 17 02') #Firmware version
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 18 02') #Factory capacity
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 20 02') #Manufacture date
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 1B 02') #Charge full cycles
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 1C 02') #Charge count
            time.sleep(0.05)
            mc.comm_simplex('55AA 03 22 01 3B 02') #Health, %
            time.sleep(0.05)

    print("Disconnecting")
    mc.disconnect()


if __name__ == "__main__":
    main()