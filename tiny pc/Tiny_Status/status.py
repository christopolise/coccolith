#!/usr/bin/env python3

"""
Quick data fetching script to populate oled display

https://github.com/christopolise/coccolith

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

# Format will be {'Name  ': [val, 1=percentage, 0=txt]}
sysinfo = {}
cpu_timer = 0
uptime_timer = 0
mem_timer = 0
num_of_cpu = 0
max_cpu_speed = 0
arch_str = ''


def fetch_mem():
    print("Mem")
    title = "Mem   "
    time.sleep(1)


def fetch_disk():
    print("disk")
    title = "Disk  "
    time.sleep(DISK_DELAY)


def fetch_cpu():
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
        percentage = float(avg_cpu_load/max_cpu_speed * 100)

        sysinfo["CPU   "] = [percentage, 1]
        sysinfo["Cores "] = [num_of_cpu, 0]
        sysinfo["Max sp"] = [max_cpu_speed, 0]
        sysinfo["Arch  "] = [arch_str, 0]

    # Can include all of the cores :D
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
                    "  "] = [int(grep_str[core]/max_cpu_speed * 100), 1]

    print(sysinfo)

    time.sleep(1)


def fetch_uptime():
    has_day = False
    has_hour = False
    has_minute = False
    uptimelist = subprocess.check_output(('uptime', '-p'))
    uptimelist = uptimelist.decode('utf-8')
    uptimelist = uptimelist.rstrip()
    uptimelist = re.sub("[^\w\s]", "", uptimelist)
    uptimelist = uptimelist.split()
    for item in uptimelist:
        if item.__contains__('day'):
            has_day = True
        elif item.__contains__('hour'):
            has_hour = True
        elif item.__contains__('minute'):
            has_minute = True

    if has_day:
        day_ind = -1
        try:
            day_ind = uptimelist.index('day') - 1
        except ValueError:
            day_ind = uptimelist.index('days') - 1
        day = uptimelist[day_ind]
    else:
        day = 0

    if has_hour:
        hour_ind = -1
        try:
            hour_ind = uptimelist.index('hour') - 1
        except ValueError:
            hour_ind = uptimelist.index('hours') - 1
        hour = uptimelist[hour_ind]
    else:
        hour = 0

    if has_minute:
        minute_ind = -1
        try:
            minute_ind = uptimelist.index('minute') - 1
        except ValueError:
            minute_ind = uptimelist.index('minutes') - 1
        minute = uptimelist[minute_ind]
    else:
        minute = 0

    sysinfo['Uptime'] = ['', 0]
    sysinfo['Day   '] = [day, 0]
    sysinfo['Hour  '] = [hour, 0]
    sysinfo['Minute'] = [minute, 0]

    print(sysinfo)
    time.sleep(1)


def to_serial():
    print("sysinfo")
    pass


def update_init():
    global CUR_STATE
    global max_cpu_speed
    global arch_str
    global num_of_cpu

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

    # Arch of CPU
    lscpuarch = subprocess.Popen(('lscpu'), stdout=subprocess.PIPE)
    arch_grep = subprocess.check_output(
        ('grep', 'Architecture'), stdin=lscpuarch.stdout)
    lscpuarch.stdout.close()
    arch_str = arch_grep.decode('utf-8')
    arch_str = arch_str.rstrip()
    arch_str = arch_str.split()[1]

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


def main():
    update_init()
    while True:
        try:
            update_tick()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
