# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 11:59:55 2019

@author: gnasses

screenscraping app for rapid network checkout of a server/device
Takes user input for hostname
Uses Netmiko library to login to devices
Ping/traceroute from core switches
Determined last L3 switch hop and infers redundant pair
uses ping/arp to determine access ports and displays selected statistics
"""
from netmiko import Netmiko
import util

try:
    print("Routine Server Network Checkout:")
    #define ELR and CTC EBR01
    dc1coreswitch1 = util.CiscoDeviceRO(host="dc1coreswitch1")
    dc2coreswitch1 = util.CiscoDeviceRO(host="dc2coreswitch1")
    ping1 = ()
    #while loop for error handling of invalid hostname, lenth arbitrarily set to 50
    while len(ping1) <= 50:
		#user input of servername to be tested
        hostname = input("Enter the Server Name to be tested: ")
        #connect to EBRs using Netmiko
        net_connect1 = Netmiko(**dc1coreswitch1.__dict__)
        net_connect2 = Netmiko(**dc2coreswitch1.__dict__)
        #ping the entered hostname        
        ping1 = net_connect1.send_command("ping " + hostname + " count 100")
        ping2 = net_connect2.send_command("ping " + hostname + " count 100")
        #print error message and restanr while loop or indicate testing in process
        if len(ping1) <= 50: 
            print ("Could not resolve servername. Please try again.")
        else: 
            print()
            print ("Testing " + hostname + "...")
    #Find the server IP
    server_ip1 = ping1.splitlines()[2].split()[3][:-1]
    server_ip2 = ping2.splitlines()[2].split()[3][:-1]
    #print ELR Results   
    print()
    print("Ping results from DC1 Network Core:")
    print("  Server IP: " + server_ip1)
    print("  Response" + ping1.splitlines()[2].split()[-2] + "ms" )
    print ("  " + ping1.splitlines()[-2])
    #print CTC Results
    print()
    print("Ping results from DC2 Network Core:")
    print("  Server IP: " + server_ip2)
    print("  Response" + ping2.splitlines()[2].split()[-2] + "ms" )
    print ("  " + ping2.splitlines()[-2])
    # Use traceroute to find last hop before server, confirm it's the same from both DCs
    trace1 = net_connect1.send_command("traceroute " + server_ip1)
    #get access switch names from traceroute
    access1 = util.acc_sw(trace1)
    #infer second switch name from first
    access2 = util.acc_pair(access1)

    print("Last Layer 3 hop to server found on: " + access1)
    print("This switch has a redundant partner: " + access2)
    print() 
except:
    print ("An exception occurred in ping testing from Core network, program exiting")
    exit()
finally:
    #done with core switches, close their connections
    net_connect1.disconnect()
    net_connect2.disconnect()

try:
    # define access switches
    my_device3 = util.CiscoDeviceRO(host=access1)
    my_device4 = util.CiscoDeviceRO(host=access2)
    #open connections to access switches
    net_connect3 = Netmiko(**my_device3.__dict__)
    net_connect4 = Netmiko(**my_device4.__dict__)
    #determine OS_Type
    nxos_check = net_connect3.send_command("show version")
    if "NX-OS" in nxos_check:
        sw_ver = "nxos"
    else:
        sw_ver = "ios"
    #ping, arp, and collect MAC addresses
    ping3 = net_connect3.send_command("ping " + server_ip1)
    ping4 = net_connect4.send_command("ping " + server_ip1)
    arp1 = net_connect3.send_command("show ip arp " + server_ip1)
    arp2 = net_connect4.send_command("show ip arp " + server_ip1)
    #different reply syntax for nexus and ios
    if sw_ver == "nxos":
        mac1 = arp1.splitlines()[-1].split()[2]
        mac2 = arp2.splitlines()[-1].split()[2]
    else: 
        mac1 = arp1.splitlines()[-1].split()[3]
        mac2 = arp2.splitlines()[-1].split()[3]
    #check if same MAC seen from both switches
    if mac1 == mac2:
        mac = mac1
        print ("Server's MAC Address is: " + mac)
        print()
    else:
        print ("Server MAC Address on " + access1 + ": " + mac1)
        print ("Server MAC Address on " + access2 + ": " + mac2)
        print()
    #find port the server MAC connects to
    show_mac_1 = net_connect3.send_command("show mac addr addr " + mac1)
    show_mac_2 = net_connect4.send_command("show mac addr addr " + mac2)
    mac1port = show_mac_1.splitlines()[-1].split()[-1]
    mac2port = show_mac_2.splitlines()[-1].split()[-1]
    #capture the port description
    portdesc1 = net_connect3.send_command("show interface description | i " + mac1port)
    portdesc2 = net_connect4.send_command("show interface description | i " + mac2port)

    #fork code to gather output properly if access switch pair is IOS or NXOS
    if sw_ver == "nxos":  
    #analyze port statistics for nexus
        if "Po" in mac1port:
            show_pc_1 = net_connect3.send_command("show port-channel data int " + mac1port + " | b Ports")
            print (access1 + " relevant port: " + mac1port)
            print ("  " + portdesc1)
            if "down" in (show_pc_1):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE DOWN!")
                print(show_pc_1)
            else:
                print("  All members of " + mac1port + " are UP!")  
                print()
                print("  Port Statistics:")
            #function to gather list of port-channel members
            pc_members = util.pc_members_nxos(show_pc_1)
            for member in pc_members:               
                print ("  " + member)
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|iscard|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[5].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[7].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil)
                # function to gather errors from member interfaces
                error_fields = util.err_fields_nxos(show_int_stats)
                errors_true = []

#needs function to sort for 0 error fields

                for error in error_fields:
                    if not error:
                        error1 = error
                    elif error.startswith('0'):
                        error1 = error
                    elif error.startswith(' 0'):
                        error1 = error
                    else: 
                        errors_true.append(error)        
                        print ("    Found: " + error)
                if not errors_true:
                    print("    No errors found!") 
        else:
            hostport1 = net_connect3.send_command("show int " + mac1port)
            print ("  " + portdesc1)
            print (hostport1)

#needs code to capture and analyze errors on a single-port connection
         
        if "Po" in mac2port:
            pc2_members = []
            show_pc_2 = net_connect4.send_command("show port-channel data int " + mac2port + " | b Ports")
            print (access2 + " relevant port: " + mac2port)
            print ("  " + portdesc2)    
            if "down" in (show_pc_2):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE DOWN!")
                print(show_pc_2)
            else:
                print("  All members of " + mac2port + " are UP!")
                print()
                print("  Port Statistics:")
            #function to gather list of port-channel members
            pc_members = util.pc_members_nxos(show_pc_2)
            for member in pc_members:                
                print ("  " + member)
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|iscard|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[5].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[7].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil)
# function to gather errors
                error_fields = util.err_fields_nxos(show_int_stats)                

#needs function to sort for 0 error fields

                errors_true = [] 
                for error in error_fields:
                    if not error:
                        error1 = error
                    elif error.startswith('0'):
                        error1 = error
                    elif error.startswith(' 0'):
                        error1 = error
                    else: 
                        errors_true.append(error)        
                        print ("    Found: " + error)
                if not errors_true:
                    print("    No errors found!")                       
        else:
            hostport2 = net_connect4.send_command("show int " + mac2port)
            print ("  " + portdesc2)  
            print (hostport2)

#needs code to capture and analyze errors on a single-port connection
 

    else:
    #analyze port-channel statistics for ios
        if "Po" in mac1port:
            show_pc_1 = net_connect3.send_command("show etherchannel " + mac1port[2:] + " summ | i " + mac1port)
            print (access1 + " relevant port: " + mac1port)
            print ("  " + portdesc1)
            if "(D)" in (show_pc_1):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE DOWN!")
                print(show_pc_1)
            if "(s)" in (show_pc_1):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE SUSPENDED!")
                print(show_pc_1)                
            else:
                print("  All members of " + mac1port + " are UP!")  
                print()
                print("  Port Statistics:")
            #function to gather list of etherchannel members
            pc_members = util.pc_members_ios(show_pc_1)
            for member in pc_members:
                print ("  " + member)
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|drop|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[8].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[10].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil)
                error_fields = util.err_fields_ios(show_int_stats)
                errors_true = []                

#needs function to sort for 0 error fields

                for error in error_fields:
                    if not error:
                        error1 = error
                    elif error.startswith('0'):
                        error1 = error
                    elif error.startswith(' 0'):
                        error1 = error
                    else:
                        errors_true.append(error)        
                if not errors_true:
                    print("    No errors found!")
                else:
                    for error in errors_true:
                        print ("    Found: " + error)
        else:
            hostport1 = net_connect3.send_command("show int " + mac1port)
            print ("  " + portdesc1)
            print (hostport1)

#needs code to capture and analyze errors on a single-port connection
 
            
        if "Po" in mac2port:
            show_pc_2 = net_connect3.send_command("show etherchannel " + mac2port[2:] + " summ | i " + mac2port)
            print (access2 + " relevant port: " + mac2port)
            print ("  " + portdesc2)
            if "(D)" in (show_pc_2):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE DOWN!")
                print(show_pc_2)
            if "(s)" in (show_pc_2):
                print("FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE SUSPENDED!")
                print(show_pc_2)                
            else:
                print("  All members of " + mac2port + " are UP!")  
                print()
                print("  Port Statistics:")
            #function to gather list of etherchannel members
            pc_members = util.pc_members_ios(show_pc_2)
            for member in pc_members:                
                print ("  " + member)
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|drop|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[8].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[10].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil)
                error_fields = util.err_fields_ios(show_int_stats)
                errors_true = []

#needs function to sort for 0 error fields

                for error in error_fields:
                    if not error:
                        error1 = error
                    elif error.startswith('0'):
                        error1 = error
                    elif error.startswith(' 0'):
                        error1 = error
                    else:
                        errors_true.append(error)        
                if not errors_true:
                    print("    No errors found!")
                else:
                    for error in errors_true:
                        print ("    Found: " + error)
        else:
            hostport2 = net_connect4.send_command("show int " + mac2port)
            print ("  " + portdesc2)
            print (hostport2)

#needs code to capture and analyze errors on a single-port connection
 

except:
    print ("An exception occurred with access network analysis!, program exiting")   

finally:    
    #close out the access switch connections
    net_connect3.disconnect()
    net_connect4.disconnect()
