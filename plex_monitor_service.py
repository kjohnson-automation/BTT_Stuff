# plex server restart

import os
import sys
import time
import datetime
import subprocess
import re

from pyservice import PyService

OFTEN = 60
NOT_SO_OFTEN = 900
HOUR = 3600
VPN_ON = False

VPN_START = 3
VPN_END = 8

PATH_FOR_SAB_CONFIG = "C:\\Users\\basil\\AppData\\Local\\sabnzbd\\sabnzbd.ini"

class plexMon(PyService):
    """ Service that monitors plex related services """
    def __init__(self, args):
        """ Calls super init """
        super().__init__(args)


def main():
    # initial check
    global VPN_ON
    tasklist = get_tasklist()
    VPN_ON = False
    running = check_plex()
    while not running:
        start_plex()
        time.sleep(60)
        print("{0}: \n\t****Plex Started****\n".format(datetime.datetime.now()))
    while True:
        try:
            wait_check()
            running = check_plex()
            if not running:
                print("{0}: \n\t****Plex found not running****\n".format(datetime.datetime.now()))
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
    if (VPN_START < current_hour < VPN_END) and (current_day not in [5, 6]):
        if not VPN_ON:
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-c"])
            VPN_ON = True
        print("{0}: Checking again in {1} minutes.".format(datetime.datetime.now(), NOT_SO_OFTEN/60))
        time.sleep(NOT_SO_OFTEN)

    else:
        tasklist = get_tasklist()
    # elif current_hour >= 16:
        current_day = datetime.datetime.now().weekday()
        if VPN_ON or (current_day in [5, 6]):
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-d"])
            VPN_ON = False
        print("{0}: Checking again in {1} minute/s.".format(datetime.datetime.now(), OFTEN/60))
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
    # running = False
    # for row in tasklist:
    #     if "Plex Media Server.exe" in row:
    #         print("Plex is running: {0}".format(datetime.datetime.now()))
    #         running = True
    #         break
    # return running
    # Refactor:
    return any(["Plex Media Server.exe" in row for row in tasklist])

def generic_tasklist_serach(search_str, tasklist):
    """ Searches the tasklisk for <search_string> """
    return any([search_str in row for row in tasklist])

def get_config(path=None):
    """ Gets sabnzbd config, and finds the schedule, uses these values for On/Off vpn """
    # Field format:
    # 1 2 3 1234567 resume
    # Enable/Disable Minute Hour DayOfTheWeek Action
    # Enabled 3:02AM EveryDay Resume
    schedule_re = r"sched.+"
    if path is None:
        path = PATH_FOR_SAB_CONFIG
    file = open(path, "r")
    config = file.read()
    file.close()
    sched = re.findall(schedule_re, config)
    if len(sched) < 1:
        print("No Schedule Found")
        return 0
    schedule = sched[0].split(",")
    for schedule_time in schedule:
        schedule_time = schedule_time.strip("schedlines = ")
        if re.match(r".+resume.+", schedule_time):
            # Sets VPN on time
            VPN_ON = 2
            schedule_time.split()
        elif re.match(r".+pause.+", schedule_time):
            # Sets VPN off time
            pass

if __name__ == '__main__':
    main()