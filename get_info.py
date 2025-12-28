"""
    .SCRIPT NAME:   get_info.py
    .DESCRIPTION:   Gets printer information (hostname, serial number, wireless config settings, etc.) of a specified printer
    .MODIFIED:      12.27.2025
    .USAGE:         py get_info.py <HOSTNAME_OR_IP>

    .UPDATES:
    - 12.27.25 - initial creation
"""

import json
import logging
import re
import socket
import sys
import time
from datetime import datetime

def query_printer(search_id, zebra_commands):
    TCP_PORT = 9100
    BUFFER_SIZE = 256
    TCP_IP = search_id

    encoded_dict = {}
    received_dict = {}

    try:
        for key, value in zebra_commands.items():
            if isinstance(value, dict):
                encoded_dict[key] = value
            else:
                encoded_dict[key] = value.encode("utf-8")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.settimeout(10)
            s.connect((TCP_IP, TCP_PORT))

            for key, value in encoded_dict:
                MESSAGE = encoded_dict[key]
                s.send(MESSAGE)
                data = s.recv(BUFFER_SIZE)
                data_received = str(data, 'utf-8')
                received_dict[key] = data_received.strip().strip('"')
                time.sleep(0.1)  # sleep to prevent out of order results (ex: ip address returned for hostname)
    except (TimeoutError, OSError, socket.timeout, socket.gaierror, socket.herror) as e:
        print(f"-- {search_param} - unable to reach - {type(e).__name__} --")
    finally:
        s.close()

    if "ZPL II" in received_dict["ZPL Mode"].upper():
        received_dict["ZPL Mode"] = "ZPL*"
    else:
        received_dict["ZPL Mode"] = "ZPL"

    received_dict["Ports"] = f"DEF: {received_dict['Default Port']} | ALT: {received_dict['Alternate Port']}"
    
    return received_dict

ZEBRA_MESSAGES = {
    "Status": "! U1 getvar \"device.status\"\r\n",
    "Hostname": "! U1 getvar \"device.friendly_name\"\r\n",
    "IP Address": "! U1 getvar \"ip.addr\"\r\n",
    "SSID": "! U1 getvar \"wlan.essid\"\r\n",
    "Model": "! U1 getvar \"device.product_name\"\r\n",
    "Serial Number": "! U1 getvar \"device.unique_id\"\r\n",
    "MAC Address": "! U1 getvar \"wlan.mac_raw\"\r\n",
    "LinkOS Version": "! U1 getvar \"appl.link_os_version\"\r\n",
    "Firmware Version": "! U1 getvar \"appl.name\"\r\n",
    "DHCP Required": "! U1 getvar \"wlan.ip.dhcp.required\"\r\n",
    "DHCP Option 81": "! U1 getvar \"ip.dhcp.option81\"\r\n",
    "WLAN Band Preference": "! U1 getvar \"wlan.band_preference\"\r\n",
    "WLAN Allowed Band": "! U1 getvar \"wlan.allowed_band\"\r\n",
    "Device Uptime": "! U1 getvar \"device.uptime\"\r\n",
    "Charging Status": "! U1 getvar \"power.chgr_status\"\r\n",
    "Default Port": "! U1 getvar \"wlan.ip.port\"\r\n",
    "Alternate Port": "! U1 getvar \"wlan.ip.port_alternate\"\r\n",
    "ZPL Mode": "! U1 getvar \"zpl.zpl_mode\"\r\n"
}

DATA_CATEGORIES = {
    "Status": ["Hostname", "Status", "Charging Status", "Device Uptime"],
    "Network": ["IP Address", "SSID", "Ports", "DHCP Required", "DHCP Option 81", "WLAN Band Preference", "WLAN Allowed Band"],
    "Hardware": ["Model", "Serial Number", "MAC Address", "ZPL Mode", "LinkOS Version", "Firmware Version"]
}

###############################
#        BEGIN  SCRIPT        #
###############################

time_start = datetime.now()  # start time

if len(sys.argv) != 2:
    print("***** INCORRECT USAGE :: MISSING ARGUMENTS *****\nScript must be ran with arguments --> py get_info.py <HOSTNAME_OR_IP>")
    sys.exit(1)

search_param = sys.argv[1].strip()

# query for hostname
try:
    if "10." in search_param:
        printer_id = search_param.strip()  # remove any spaces
    else:
        printer_id = socket.gethostbyname(search_param)
except (socket.gaierror) as e:
    print(f"-- {search_param} :: unknown host :: {type(e).__name__}: {e} --")
    sys.exit(1)

printer_data = query_printer(printer_id, ZEBRA_MESSAGES)

for key in printer_data:
    if key in ["Status", "MAC Address"]:
        printer_data[key] = str(printer_data.get(key, "")).upper()

for category, keys in DATA_CATEGORIES.items():
    print(f"{category.upper()}\n--------------------------------------------------")
    for key in keys:
        if key in ["Default Port", "Alternate Port"]:
            pass
        value = printer_data.get(key, "")
        print(f"{key.ljust(25, '.')} {value}")
    print("\n", end='')

time_end = datetime.now()  # end time

###############################
#         END  SCRIPT         #
###############################

# calculate script duration
duration = time_end - time_start
total_seconds = int(duration.total_seconds())
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60
formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

print(f"DURATION: {formatted_duration}")