# plex server restart

import os
import sys
import time
import datetime
import subprocess
import re

OFTEN = 60
NOT_SO_OFTEN = 900
HOUR = 3600
VPN_ON = False
OMBI_ON = False
OMBI_CHECK = False

def main():
    # initial check
    global VPN_ON
    global OMBI_ON
    global OMBI_CHECK
    tasklist = get_tasklist()
    OMBI_ON = ombi_search(tasklist)[0]
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
    global OMBI_ON
    current_hour = datetime.datetime.now().hour
    current_day = datetime.datetime.now().weekday()
    # Checks to see if its between 2AM and 4PM During the Week, if so VPN is enabled.
    if (2 < current_hour < 16) and (current_day not in [5, 6]):
        if not VPN_ON:
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-c"])
            VPN_ON = True
        if OMBI_ON and OMBI_CHECK:
            toggle_ombi(0) 
        print("{0}: Checking again in {1} minutes.".format(datetime.datetime.now(), NOT_SO_OFTEN/60))
        time.sleep(NOT_SO_OFTEN)

    else:
        tasklist = get_tasklist()
        OMBI_ON = ombi_search(tasklist)[0]
    # elif current_hour >= 16:
        current_day = datetime.datetime.now().weekday()
        if VPN_ON or (current_day in [5, 6]):
            subprocess.run(["C:\\Program Files (x86)\\NordVPN\\nordvpn", "-d"])
            VPN_ON = False
        if not OMBI_ON and OMBI_CHECK:
            toggle_ombi(1)
        print("{0}: Checking again in {1} minute/s.".format(datetime.datetime.now(), OFTEN/60))
        time.sleep(OFTEN)

def check_plex():
    """ Just combines get_tasklist and plex_search to reduce code """
    tasklist = get_tasklist()
    return plex_search(tasklist)

def check_ombi():
    tasklist = get_tasklist()
    return ombi_search(tasklist)

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

def ombi_search(tasklist):
    """ Searches tasklist for ombi and starts if its not running """
    running = False
    pid_regex = r".+\.exe\s+([0-9]+)\s+\w+"
    pid = "N/A"
    for row in tasklist:
        if "Ombi.exe" in row:
            pid = re.findall(pid_regex, row)
    return [running, pid]

def toggle_ombi(toggle:bool):
    """ Turns off or on ombi """
    tasklist = get_tasklist
    [ombi_on, pid] = ombi_search(tasklist)
    if not ombi_on and toggle:
        os.popen("C:\\Users\\basil\\ombi\\Ombi.exe")
        return 0
    elif ombi_on and not toggle:
        print("Killing Ombi")
        # TODO: implement kill ombi
        return 1
    # returns -1 for no activity
    return -1


if __name__ == '__main__':
    main()