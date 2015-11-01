#!/usr/bin/env python3

"""
#=============================================================================#

FILE            : check_spideroak.py

DESCRIPTION     : Nagios plugin to check SpiderOak free space.

REQUIREMENTS    : SpiderOak.  Tested with v4.1.9860
BUGS            : Search for XXX in the script.
NOTES           : Due to the change from long / int in Python 2.6
                    to just int in Python 3, this script will need some
                    modifiacations if you want to use Python 2.6
AUTHOR(s)       : Martinus Nel (martinus.nel@gmail.com)
                : Tim Berry (timhberry@gmail.com)
CREATED         : 05-12-2011
WISH LIST       : Multiple checks at the same time

2012-05-27 Tim Berry - 1.4
           Changed input and output of integers to calculate MB.
           Changed from switches to a mode selector.
           Added percentage mode.

Copyright (C) 2011 Martinus Nel
  This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#=============================================================================#
"""

import sys
import optparse
import os
import ast

#====================#
# Nagios exit status #
#====================#
StateOK = 0
StateWarning = 1
StateCritical = 2
StateUnknown = 3
StateDependent = 4

#==================#
# Global variables #
#==================#
Version = 1.4
Description = """Description: This is a Nagios check to see how space is
used on your SpiderOak account."""

#===========#
# Functions #
#===========#
def CheckTotal(CurrentTotal, WarningLevel, CriticalLevel):
    if CurrentTotal < WarningLevel:
        print("Total Space OK - current usage :%.3fMB"
        % (CurrentTotal / 1048576), "|Used=%.3f MB" % (CurrentTotal / 1048576))
        sys.exit(StateOK)
    elif CurrentTotal < CriticalLevel:
        print("Total Space Warning - current usage :%.3fMB"
        % (CurrentTotal / 1048576), "|Used=%.3f MB" % (CurrentTotal / 1048576))
        sys.exit(StateWarning)
    else:
        print("Total Space Critical - current usage :%.3fMB"
        % (CurrentTotal / 1048576), "|Used=%.3f MB" % (CurrentTotal / 1048576))
        sys.exit(StateCritical)

def CheckDevice(WarningLevel, CriticalLevel, Device, AllDevices):
    FoundDevice = False
    for i in AllDevices:
        if Device == i['device_desc']:
            FoundDevice = True
            if i['storage_used'] < WarningLevel:
                print(Device, "Space OK - current usage :%.3fMB"
                % (i['storage_used'] / 1048576), "|Used=%.3f MB"
                % (i['storage_used'] / 1048576))
                sys.exit(StateOK)
            elif i['storage_used'] < CriticalLevel:
                print(Device, "Space Warning - current usage :%.3fMB"
                % (i['storage_used'] / 1048576), "|Used=%.3f MB"
                % (i['storage_used'] / 1048576))
                sys.exit(StateWarning)
            else:
                print(Device, "Space Critical - current usage :%.3fMB"
                % (i['storage_used'] / 1048576), "|Used=%.3f MB"
                % (i['storage_used'] / 1048576))
                sys.exit(StateCritical)
    if not FoundDevice:
        print("Device '", Device, "' not found !")
        sys.exit(StateCritical)

def CheckCategory(WarningLevel, CriticalLevel, Category, AllCategories):
    if Category not in AllCategories:
        print("Category '", Category, "' not found !")
        sys.exit(StateCritical)
    elif AllCategories[Category] < WarningLevel:
        print(Category, "Space OK - current usage :%.3fMB" 
        % (AllCategories[Category] / 1048576), "|Used=%.3f MB" 
        % (AllCategories[Category] / 1048576))
        sys.exit(StateOK)
    elif AllCategories[Category] < CriticalLevel:
        print(Category, "Space Warning - current usage :%.3fMB" 
        % (AllCategories[Category] / 1048576), "|Used=%.3f MB" 
        % (AllCategories[Category] / 1048576))
        sys.exit(StateWarning)
    else:
        print(Category, "Space Critical - current usage :%.3fMB" 
        % (AllCategories[Category] / 1048576), "|Used=%.3f MB" 
        % (AllCategories[Category] / 1048576))
        sys.exit(StateCritical)
        
def CheckPercentTotal(CurrentTotal, WarningLevel, CriticalLevel, Quota):
    Quota *= 1048576
    PercentUsed = (1.0*CurrentTotal/Quota)*100
    if PercentUsed < WarningLevel:
        print("Total Space OK - current usage :%.3fMB" 
        % (CurrentTotal / 1048576), "|Used=%.3f MB" 
        % (CurrentTotal / 1048576), "|Percent:%.2f" % PercentUsed)
        sys.exit(StateOK)
    elif PercentUsed < CriticalLevel:
        print("Total Space Warning - current usage :%.3fMB" 
        % (CurrentTotal / 1048576), "|Used=%.3f MB" 
        % (CurrentTotal / 1048576), "|Percent:%.2f" % PercentUsed)
        sys.exit(StateWarning)
    else:
        print("Total Space Critical - current usage :%.3fMB" 
        % (CurrentTotal / 1048576), "|Used=%.3f MB" 
        % (CurrentTotal / 1048576), "|Percent:%.2f" % PercentUsed)
        sys.exit(StateCritical)
        
#======#
# Main #
#======#
def main():
    
    parser = optparse.OptionParser(version="%prog version 1.4",
             description=Description, usage="""%prog -m MODE [-c Category] [-d Device] [-q] -W INT -C INT

In percent mode, specify thresholds as percentages. Otherwise
specify thresholds in MB. Examples:

./check_spideroak.py -m total -W 3072 -C 5120
  Checks total usage, warns if over 3072MB, critical if over 5120MB.

./check_spideroak.py -m device -d mylaptop -W 1024 -C 2048
  Check usage of 'mylaptop', warn at 1024MB, critical at 2048MB.
  
./check_spideroak.py -m percent -q 8192 -W 80 -C 90
  Check total usage, specifying quota of 8GB. Warn at 80%, critical at 90%.""")
    parser.add_option("-m", "--mode", dest="Mode", default="total",
           help="""Specify the mode of operation. Options are:
           total, percent, category or device""")
    parser.add_option("-c", "--category", dest="Category",
           help="Specify a category (used with category mode)")
    parser.add_option("-d", "--device", dest="Device",
           help="Specify a device (used with device mode)")
    parser.add_option("-q", "--quota", dest="Quota", type='int', default=5120,
           help="Specify your total SpiderOak quota (defaults to 5GB)")
    parser.add_option("-W", "--warning", dest="WarningLevel", type='int',
           help="Warning level of data used. Must be less than critical.")
    parser.add_option("-C", "--critical", dest="CriticalLevel", type='int',
           help="Critical level of data used. Must be more than warning.")

    # The logical ordering will need a complete re-work if percentages are
    # introduced, to enable multiple options used together.
    # Or even no options to run everything.
    (Opts, Args) = parser.parse_args()

    if not Opts.WarningLevel or not Opts.CriticalLevel:
        print("CRITICAL: Both warning and critical values must be supplied.")
        sys.exit(StateCritical)
    elif Opts.WarningLevel >= Opts.CriticalLevel:
        print("CRITICAL: Critical must be more than warning.")
        sys.exit(StateCritical)
        
    if Opts.CriticalLevel > 100 and Opts.Mode is "percent":
        # Don't need to check Opts.WarningLevel, we already know it's 
        # below Opts.CriticalLevel at this point
        print("CRITICAL: You cannot specify thresholds above 100% in percentage mode.")
        sys.exit(StateCritical)

    Pipe = os.popen('/usr/bin/SpiderOak --space')
    SpiderOut = Pipe.readlines()
    ExitStatus = Pipe.close()
    # I'm not sure under which condition the above exit status would not be
    # 'none', so I have no test in place right now for it.

    # For debugging, simply comment out the above 3 lines of code,
    # and use this test variable.
    #SpiderOut = ['Recalculating space usage (this may take a moment...)\n', "Space usage by category: {'': 20792934558L, 'Documents': 129539767, 'MusicL': 340798563, u'Deleted Folders': 108966}\n", "Space usage by device: [{'storage_used': 14019360377L, 'device_desc': u'Blue', 'device_id': 3}, {'storage_used': 233893, 'device_desc': u'Work Laptop', 'device_id': 1}]\n", 'Space of all stored files (if uncompressed and not deduplicated): 51771775477L\n']

    # Well, either I butcher the list or I use regex.  Both looks rather ugly.
    # No idea what else I can do :(
    # Since SpiderOak currently uses Python 2.x, it prints 'L' for 'long'
    #  numbers.  Python 3 no longer uses 'long'.
    CurrentTotal = int(str(SpiderOut[-1].split(':')[-1]).replace('L', ''))

    # I have NO idea why SpiderOak adds a 'u' in front of the device name
    #  or deleted folders.
    # Replace 'L,' with ',' in case there is a 'L' in the dictionary key.
    AllCategories = ast.literal_eval(str(SpiderOut[1].split('category:')[-1]).rstrip().lstrip().replace(', u', ', ').replace('L,', ','))
    AllDevices = ast.literal_eval(str(SpiderOut[2].split('device:')[-1]).rstrip().lstrip().replace(': u', ': ').replace('L,', ','))

    if "percent" not in Opts.Mode:
        Opts.WarningLevel *= 1048576
        Opts.CriticalLevel *= 1048576
    
    if "total" in Opts.Mode:
        CheckTotal(CurrentTotal, Opts.WarningLevel, Opts.CriticalLevel)
    elif "percent" in Opts.Mode:
        CheckPercentTotal(CurrentTotal, Opts.WarningLevel, Opts.CriticalLevel, 
        Opts.Quota)
    elif "category" in Opts.Mode:
        CheckCategory(Opts.WarningLevel, Opts.CriticalLevel, Opts.Category, 
        AllCategories)
    elif "device" in Opts.Mode:
        CheckDevice(Opts.WarningLevel, Opts.CriticalLevel, Opts.Device, 
        AllDevices)
    else:
        print("CRITICAL: You must specify a valid MODE of operation.")
        sys.exit(StateCritical)
            
if __name__ == '__main__':
    main()
