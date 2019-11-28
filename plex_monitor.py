# plex server restart

import os
import sys
import time
import datetime
import subprocess

OFTEN = 60
NOT_SO_OFTEN = 900
HOUR = 3600
VPN_ON = False

def main():
    # initial check
    global VPN_ON
    VPN_ON = False
    running = check_plex()
    while not running:
        start_plex()
        time.sleep(60)
        print("Plex Started: {0}".format(datetime.datetime.now()))
    while True:
        try:
            wait_check()
            running = check_plex()
            if not running:
                print("Plex found not running: {0}".format(datetime.datetime.now()))
                start_plex()
        except KeyboardInterrupt:
            print("Exiting Monitor - plex is no longer being monitored.")
            sys.exit(0)

def start_plex():
    """ starts plex service again after being found not running """
    print("Staring Plex: {0}".format(datetime.datetime.now()))
    os.popen("C:\\Program Files (x86)\\Plex\\Plex Media Server\\Plex Media Server.exe")

def wait_check():
    """ Depending on what time it is, it'll timeout between queries """
    global VPN_ON
    current_hour = datetime.datetime.now().hour
    current_day = datetime.datetime.now().weekday()
    # Checks to see if its between 2AM and 4PM During the Week, if so VPN is enabled.
    if (2 < current_hour < 16) and (current_day not in [5, 6]):
        if not VPN_ON:
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-c"])
            VPN_ON = True
        print("Checking again in {0} minutes.".format(NOT_SO_OFTEN/60))
        time.sleep(NOT_SO_OFTEN)

    else:
    # elif current_hour >= 16:
        current_day = datetime.datetime.now().weekday()
        if VPN_ON or (current_day in [5, 6]):
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-d"])
            VPN_ON = False
        print("Checking again in {0} minute/s.".format(OFTEN/60))
        time.sleep(OFTEN)

def check_plex():
    """ Just combines get_tasklist and plex_search to reduce code """
    tasklist = get_tasklist()
    return plex_search(tasklist)

def get_tasklist():
    """ Used to retrieve and parse tasklist to monitor """
    return os.popen("tasklist").read().split("\n")

def plex_search(tasklist):
    """ Used to search the tasklist for "Plex Media Server.exe" """
    running = False
    for row in tasklist:
        if "Plex Media Server.exe" in row:
            print("Plex is running: {0}".format(datetime.datetime.now()))
            running = True
            break
    return running


if __name__ == '__main__':
    main()