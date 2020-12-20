#!/usr/bin/env python3

"""
Quick data fetching script to populate oled display

https://github.com/christopolise/oled_sysfetch

AUTHORED BY: Chris Kitras
LAST DATE MODIFIED: 2020-12-20

"""

import subprocess
import re
import time

MAX_LINE = 4  # Number of lines the OLED supports
CUR_STATE = 0
MEM_STATE = 1
DISK_STATE = 2
CPU_STATE = 3
UPTIME_STATE = 4
CPU_TIMER_MAX = 5
UPTIME_TIMER_MAX = 5
MEM_TIMER_MAX = 5
DISK_DELAY = 5

cpu_timer = 0
uptime_timer = 0
mem_timer = 0

# Get number of CPUs on system
cpusinfo = subprocess.Popen(
    ('cat', '/proc/cpuinfo'), stdout=subprocess.PIPE)
greplast = subprocess.Popen(
    ('grep', 'processor'), stdin=cpusinfo.stdout, stdout=subprocess.PIPE)
cpusinfo.stdout.close()
taillast = subprocess.check_output(
    ('tail', '-1'), stdin=greplast.stdout)
greplast.stdout.close()
string = taillast.decode('utf-8')
num_of_cpu = int(string.split()[2]) + 1  # Add to compensate for zero index

# Obtain advertised speed of CPU
lscpuinfo = subprocess.Popen(('lscpu'), stdout=subprocess.PIPE)
grepspeed = subprocess.check_output(
    ('grep', 'CPU max MHz'), stdin=lscpuinfo.stdout)
lscpuinfo.stdout.close()
string2 = grepspeed.decode('utf-8')
max_cpu_speed = int(float(string2.split()[3]))


sysinfo = {}


def fetch_mem():
    print("Mem")
    title = "Mem   "
    time.sleep(1)


def fetch_disk():
    print("disk")
    title = "Disk  "
    time.sleep(DISK_DELAY)


def fetch_cpu():
    print("cpu")
    # Check to see if there are more than 4 CPUs (zero indexed)

    # Too big for screen, only report average
    if num_of_cpu > MAX_LINE:
        cpu_mhz_line = subprocess.Popen(
            ('lscpu'), stdout=subprocess.PIPE)
        grep_cpu_load = subprocess.check_output(
            ('grep', 'CPU MHz'), stdin=cpu_mhz_line.stdout)
        cpu_mhz_line.stdout.close()
        load_str = grep_cpu_load.decode('utf-8')
        load_str = load_str.rstrip()
        avg_cpu_load = max_cpu_speed - float(re.sub("[^0-9.]", "", load_str))
        percentage = int(avg_cpu_load/max_cpu_speed * 100)
        sysinfo["CPU   "] = percentage

    else:
        cpu_group = subprocess.Popen(
            ('cat', '/proc/cpuinfo'), stdout=subprocess.PIPE)
        grep_group = subprocess.check_output(
            ('grep', 'cpu MHz'), stdin=cpu_group.stdout)
        cpu_group.stdout.close()
        grep_str = grep_group.decode('utf-8')
        grep_str = grep_str.rstrip()
        grep_str = grep_str.split('\n')
        for core in range(len(grep_str)):
            grep_str[core] = max_cpu_speed - \
                float(re.sub("[^0-9.]", "", grep_str[core]))
            sysinfo["CPU" + str(core) +
                    "  "] = int(grep_str[core]/max_cpu_speed * 100)

        print(sysinfo)

    time.sleep(1)


def fetch_uptime():
    print("uptime")
    title = "uptime"
    time.sleep(1)


def to_serial():
    print("sysinfo")
    pass


def update_init():
    global CUR_STATE
    CUR_STATE = 1


def update_tick():
    global CUR_STATE
    global cpu_timer
    global mem_timer
    global uptime_timer
    sysinfo.clear()

    # Mealy Actions
    if (CUR_STATE == MEM_STATE):
        if mem_timer == MEM_TIMER_MAX:
            mem_timer = 0
            CUR_STATE = DISK_STATE
    elif(CUR_STATE == DISK_STATE):
        CUR_STATE = CPU_STATE
    elif(CUR_STATE == CPU_STATE):
        if cpu_timer == CPU_TIMER_MAX:
            cpu_timer = 0
            CUR_STATE = UPTIME_STATE
    elif(CUR_STATE == UPTIME_STATE):
        if uptime_timer == UPTIME_TIMER_MAX:
            uptime_timer = 0
            CUR_STATE = MEM_STATE

    # Moore Actions
    if (CUR_STATE == MEM_STATE):
        mem_timer += 1
        fetch_mem()
    elif(CUR_STATE == DISK_STATE):
        fetch_disk()
    elif(CUR_STATE == CPU_STATE):
        cpu_timer += 1
        fetch_cpu()
    elif(CUR_STATE == UPTIME_STATE):
        uptime_timer += 1
        fetch_uptime()

    to_serial()


def main():
    update_init()
    while True:
        try:
            update_tick()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
