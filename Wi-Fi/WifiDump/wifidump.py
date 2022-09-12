#! /bin/env python3

from scapy.all import *
from threading import Thread
import time
import pandas
import os
import sys
import re
import subprocess


def find_nic():
    wlan_code = re.compile("Interface (wl[a-z0-9]+)")
    result = subprocess.run(["iw", "dev"], capture_output=True).stdout.decode()
    network_interface_controllers = wlan_code.findall(result)

    return network_interface_controllers


def sudo_check():
    # Check if the user is running as root or using sudo
    if not "SUDO_UID" in os.environ.keys():
        print("Run with sudo")
        exit()


def monitor_mode():

    current_state = subprocess.getoutput(
        "iwconfig 2>/dev/null | grep Mode | awk '{print $1}'")
    adapt_name = find_nic()
    adapt_name = adapt_name[0]

    # System command to put network card into monitor mode
    if current_state == "Mode:Managed":

        os.system(f"ip link set {adapt_name} down")
        os.system(f"iw {adapt_name} set monitor none")
        os.system(f"ip link set {adapt_name} up")

    # System commands to put network card into managed mode
    elif current_state == "Mode:Monitor":

        os.system(f"ip link set {adapt_name} down")
        os.system(f"iwconfig {adapt_name} mode managed")
        os.system(f"ip link set {adapt_name} up")


def network_sniffer():
    try:

        networks = pandas.DataFrame(
            columns=["BSSID", "SSID", "dBm_Signal", "Channel", "ENC/AUTH"])

        # set the index BSSID (MAC address of the AP)
        networks.set_index("BSSID", inplace=True)

        def callback(packet):

            if packet.haslayer("Dot11Beacon"):

                # extract the MAC address of the network
                bssid = packet["Dot11"].addr2

                # get the name of it
                ssid = packet["Dot11Elt"].info.decode()

                try:
                    dbm_signal = packet.dBm_AntSignal

                except:
                    dbm_signal = "N/A"

                # extract network stats
                stats = packet["Dot11Beacon"].network_stats()

                # get the channel of the AP
                channel = stats.get("channel")

                # get the crypto
                crypto = stats.get("crypto")

                networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)

        def print_all():

            while True:
                print(networks)
                time.sleep(0.7)
                os.system("clear")

        # start the thread that prints all the networks
        printer = Thread(target=print_all)
        printer.daemon = True
        printer.start()

        # start sniffing
        adapt_name = find_nic()
        adapt_name = adapt_name[0]
        sniff(prn=callback, iface=adapt_name)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":

    sudo_check()

    current_state = subprocess.getoutput(
        "iwconfig 2>/dev/null | grep Mode | awk '{print $1}'")

    if current_state == "Mode:Managed":
        monitor_mode()

    network_sniffer()
    monitor_mode()
