# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 08:09:00 2019

@author: gnasses

Collection of functions for use with servervalidation.py screenscraping app
"""
#class object for use with Netmiko with RO automation creds as defaults
class CiscoDeviceRO:
    def __init__(self, host, username='<insert username>', password='<insert password>', device_type='cisco_ios'):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type

# Get access switch name from traceroute
def acc_sw(trace):
    hop = -1
    while 'mls' not in trace.splitlines()[hop]:
        hop = (hop -1)
        if hop == -10:
            break
    if 'mls' in trace.splitlines()[hop]:
        tracesplit = trace.splitlines()[hop].split()
        access1 = tracesplit[1].split('-')[0]
    else:
        access1 = "UNABLE TO TRACE"
    return access1

#find redundant pair switch name given name of either switch in the pair
def acc_pair(switch):
    if switch == "UNABLE TO TRACE":
        access2 = "UNABLE TO TRACE"
    else:
        accessnum = int(switch[-1:])
        if accessnum % 2 == 0:
            access2 = switch[:-1] + str(accessnum -1)
        else:
            access2 = switch[:-1] + str(accessnum +1)
    return access2


"""
Need function(s) to work out port channel analysis
"""
#function finds nxos port channel members from "show port-channel data int " + po# + " | b Ports"
def pc_members_nxos(show_pc):
    pc_members = []
    pclines = show_pc.splitlines()
    member_num = (len(pclines) - 2)
    while member_num >= 1:
        pcsplit = pclines[member_num].split()
        pcport = pcsplit[0]
        pc_members.append(pcport)
        member_num = (member_num - 1)
    while member_num == 0: 
        pcsplit = pclines[member_num].split()
        pcport = pcsplit[1]
        pc_members.append(pcport)
        member_num = (member_num - 1)
    return pc_members

#function finds ios etherchannel members from "show etherchannel " + port[2:] + " summ | i " + port"
def pc_members_ios(show_pc):
    pc_members = []
    pcsplit = show_pc.split()
    member_num = len(pcsplit)
    while member_num >= 4:
        pcport = pcsplit[member_num - 1][:-3]
        pc_members.append(pcport)
        member_num = (member_num - 1)
    return pc_members


def err_fields_ios(show_int_stats):
    error_fields = []
    errors_true = []
    error_fields.extend(show_int_stats.splitlines()[2].strip().split(','))
    error_fields.extend(show_int_stats.splitlines()[3].strip().split(','))
    return error_fields
#    for error in error_fields:
#        if not error:
#            error1 = error
#        elif error.startswith('0'):
#            error1 = error
#        elif error.startswith(' 0'):
#            error1 = error
#        else:
#            errors_true.append(error)
#        return errors_true
    
def err_fields_nxos(show_int_stats):
    error_fields = []
    error_fields.extend(show_int_stats.splitlines()[1].split('  '))
    error_fields.extend(show_int_stats.splitlines()[2].split('  '))
    error_fields.extend(show_int_stats.splitlines()[3].split('  '))
    error_fields.extend(show_int_stats.splitlines()[4].split('  '))
    return error_fields

""" 
function below not working during testing
  
def err_disp_nxos(error_fields):
    errors_true = []
    for error in error_fields:
        if not error:
            err1 = ()
        elif error.startswith('0'):
            err1 = ()
        elif error.startswith(' 0'):
            err1 = ()
        else:
            errors_true.append(error)
        return errors_true
#            print ("    Found: " + error)
#        if not errors_true:
#            print("    No errors found!")
""" 
