#! /bin/env python3

from scapy.all import *
from threading import Thread
import time
import pandas
import os
import re
import subprocess

# Find network interface and return name of interface
def find_nic():
    wlan_code = re.compile("Interface (wl[a-z0-9]+)")
    result = subprocess.getoutput("iw dev")
    network_interface_controllers = wlan_code.findall(result)

    return network_interface_controllers

# Check if wireless interface is in monitormode or not
def check_monitor_mode():
    monitor_code = re.compile("type monitor")
    result = subprocess.getoutput("iw dev")
    monitor_mode_results = monitor_code.findall(result)

    if monitor_mode_results == []:
        return False
    else:
        return True

# Check if user is running as sudo or root
def sudo_check():
    if not "SUDO_UID" in os.environ.keys():
        print("Run with sudo")
        exit()

# Enable/Disable monitor mode
def monitor_mode():
    # System command to put network card into monitor mode
    if not check_monitor_mode():
        os.system(f"ip link set {adapt_name} down")
        os.system(f"iw {adapt_name} set monitor none")
        os.system(f"ip link set {adapt_name} up")

    # System commands to put network card into managed mode
    else:
        os.system(f"ip link set {adapt_name} down")
        os.system(f"iwconfig {adapt_name} mode managed")
        os.system(f"ip link set {adapt_name} up")

# Sniff network packets for dot11 beacons and sort into a dataframe
def network_sniffer():
    try:
        networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "ENC/AUTH"])

        # Set the index BSSID (MAC address of the AP)
        networks.set_index("BSSID", inplace=True)

        # Sort through packet and updating dataframe 
        def callback(packet):

            if packet.haslayer("Dot11Beacon"):

                # Extract the MAC address of the network
                bssid = packet["Dot11"].addr2

                # Get the name of it
                ssid = packet["Dot11Elt"].info.decode()

                try:
                    dbm_signal = packet.dBm_AntSignal

                except:
                    dbm_signal = "N/A"

                # get stats
                stats = packet["Dot11Beacon"].network_stats()
                
                # Get the channel
                channel = stats.get("channel")
                
                # Get crypto
                crypto = stats.get("crypto")

                networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)

        def print_all():
            while True:
                print(networks)
                time.sleep(0.7)
                os.system("clear")

        # Start the thread that prints all the networks
        printer = Thread(target=print_all)
        printer.daemon = True
        printer.start()

        # Start sniffing
        sniff(prn=callback, iface=adapt_name)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":

    find_adapt_name = find_nic()
    if find_adapt_name == []:
        print("Error: No wireless network interface detected.")
        exit()
    
    adapt_name = find_adapt_name[0]

    sudo_check()

    if not check_monitor_mode():
        monitor_mode()

    network_sniffer()
    monitor_mode()
