import time
import datetime
import threading

# When to start allowing websites
open_trigger_time = datetime.time(14, 43, 0)

# When to stop allowing websites
close_trigger_time = datetime.time(14, 44, 0)

# Checks if hosts file has been edited and changes it back if it has
# This is in seconds
check_time_dt = 1

# string infos
local_host = "127.0.0.1"
string_base = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost

127.0.0.1 www.instagram.com
127.0.0.1 www.facebook.com
127.0.0.1 krunker.io
127.0.0.1 slither.io
127.0.0.1 agar.io"""

# File name
file_name = "C:\\Windows\\System32\\drivers\\etc\\hosts"
# file_name = "test.txt"

# Backup - allows us to check if the file has been changed
string_backup = open(file_name, "r").read()

# Permanently banned sites, CSV style
string_banned = ""

# Blocked sites, CSV style
string_blocked = ""

# Prevents multiple trigger messages from appearing
blocked = True

# True when the program needs to die
kill = False


# Takes user input and modifies the banned or blocked lists.
def user_input():
    global string_banned, string_blocked, kill
    while True:
        user_string = input("\'q\' to quit, \'addban\' to ban, \'addblock\' to block\n")
        if user_string == "q":
            kill = True
            break
        elif user_string == "addban":
            user_string = input("paste url or \'c\' to cancel:\n")
            if not user_string == 'c':
                string_banned = string_banned + "," + user_string
            else:
                print("Input error, please type in option")
        elif user_string == "addblock":
            user_string = input("paste url or \'c\' to cancel:\n")
            if not user_string == 'c':
                string_blocked = string_blocked + "," + user_string
            else:
                print("Input error, please type in option")
        else:
            print("Input error, please type in option")


# Checks time to see whether blocked should be unblocked
def check_time():
    global blocked, kill
    while True:
        current_time = datetime.datetime.now().time()

        if kill:
            break

        if open_trigger_time > close_trigger_time:
            print("Invalid input times")
        else:
            if open_trigger_time < current_time < close_trigger_time and blocked:
                print("Things are unblocked!!!")
                blocked = False
            elif (current_time > close_trigger_time or current_time < open_trigger_time) and not blocked:
                print("Everything is blocked :(")
                blocked = True

        time.sleep(check_time_dt)


# Takes string banned and blocked and saves them to hosts file
def modify_hosts():
    global string_banned, string_blocked, string_base, string_backup, kill
    while True:
        if kill:
            write_when_blocked()
            break

        hosts = open(file_name, "r")
        if not hosts.read() == string_backup:
            print("A user has modified the file, changing to backup")
            hosts.close()
            hosts = open(file_name, "w")
            hosts.write(string_backup)
        hosts.close()

        if blocked:
            write_when_blocked()
        else:
            string_total = string_base

            array_banned = string_banned.split(",")
            string_total = string_total + "\n\n"
            for string_val in array_banned:
                if string_val != "":
                    string_total = string_total + local_host + " " + string_val + "\n"

            hosts = open(file_name, "w")
            hosts.write(string_total)
            hosts.close()
            string_backup = string_total

        time.sleep(check_time_dt)


# Write code for when blocked
def write_when_blocked():
    global string_banned, string_blocked, string_base, string_backup
    string_total = string_base

    array_banned = string_banned.split(",")
    array_blocked = string_blocked.split(",")
    string_total = string_total + "\n\n"
    string_total = string_total + "# Banned\n\n"
    for string_val in array_banned:
        if string_val != "":
            string_total = string_total + local_host + " " + string_val + "\n"

    string_total = string_total + "\n\n# Blocked\n\n"
    for string_val in array_blocked:
        if string_val != "":
            string_total = string_total + local_host + " " + string_val + "\n"

    hosts = open(file_name, "w")
    hosts.write(string_total)
    hosts.close()
    string_backup = string_total


# Parses previous file so it can remember which files to ban or block
def read_on_start():
    global string_banned, string_blocked, local_host
    print("Parsing Hosts File")
    hosts = open(file_name, "r")
    hosts_data = hosts.read()
    hosts.close()

    if not (hosts_data.find("# Banned") == -1 or hosts_data.find("# Blocked") == -1):
        index_ban = hosts_data.index("# Banned")
        index_block = hosts_data.index("# Blocked")

        hosts_banned = hosts_data[index_ban:index_block]
        hosts_blocked = hosts_data[index_block:]

        hosts_banned = hosts_banned.split("\n")
        hosts_blocked = hosts_blocked.split("\n")

        for string_val in hosts_banned:
            if not (string_val == "" or string_val == "# Banned"):
                if string_banned == "":
                    string_banned = string_val[string_val.index(local_host) + len(local_host) + 1:]
                else:
                    string_banned = string_banned + "," + string_val[string_val.index(local_host) + len(local_host) + 1:]

        for string_val in hosts_blocked:
            if not (string_val == "" or string_val == "# Blocked"):
                if string_blocked == "":
                    string_blocked = string_val[string_val.index(local_host) + len(local_host) + 1:]
                else:
                    string_blocked = string_blocked + "," + string_val[string_val.index(local_host) + len(local_host) + 1:]


if __name__ == "__main__":
    # Parses file to initialize variables (allows saving of banned and blocked items)
    read_on_start()
    # Starting the threads for each process
    t_user_input = threading.Thread(target=user_input, name='t_user_input')
    t_check_time = threading.Thread(target=check_time, name='t_check_time')
    t_modify_hosts = threading.Thread(target=modify_hosts, name='t_modify_hosts')

    # starting threads
    t_user_input.start()
    t_check_time.start()
    t_modify_hosts.start()

    # wait until all threads finish
    t_user_input.join()
    t_check_time.join()
    t_modify_hosts.join()
