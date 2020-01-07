#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import sys
import site
import datetime
from netmiko import Netmiko
import util
import os.path
import cgi
import cgitb
cgitb.enable()
form = cgi.FieldStorage()
hostname = form.getfirst('content1')
print("Content-Type: text/html\n\n")
print ("<h2> Network Test Results </h2>")
print ("Hostname: " + hostname + "<br />")
print ("<br />")
print ("Date and time of Analysis:<br />")
now = str(datetime.datetime.now())
print (now)
print ("</br />")
try:
    print ("<b>Basic Server/Device Network Validation Routine</b> <br />")
    #define ELR and CTC EBR01
    dc1core01 = util.CiscoDeviceRO(host="dc1core01")
    dc2core01 = util.CiscoDeviceRO(host="dc2core01")
    ping1 = ()
    #while loop for error handling of invalid hostname, lenth arbitrarily set to 50
    while len(ping1) <= 50:
        #connect to EBRs using Netmiko
        net_connect1 = Netmiko(**dc1core01.__dict__)
        net_connect2 = Netmiko(**dc2core01.__dict__)
        print ("<br />")        
        #ping the entered hostname        
        ping1 = net_connect1.send_command("ping " + hostname + " count 100")
        ping2 = net_connect2.send_command("ping " + hostname + " count 100")
        #print error message and restanr while loop or indicate testing in process
        if len(ping1) <= 50: 
            print ("Could not resolve servername. Please try again.")
        else: 
            print("<br />")
            print ("Testing " + hostname + "..." + "<br />")
            print("<br />")
    #Find the server IP
    print ("pings completed")
    server_ip1 = ping1.splitlines()[2].split()[3][:-1]
    server_ip2 = ping2.splitlines()[2].split()[3][:-1]
    #print ELR Results
    print()
    print("<b>Ping results from Elk River Network Core: </b><br />")
    print("  Server IP: " + server_ip1 + "<br />")
    print("  Response" + ping1.splitlines()[2].split()[-2] + "ms" + "<br />")
    print ("  " + ping1.splitlines()[-2] + "<br />")
    print ("<br />")
    #print CTC Results
    print()
    print("<b>Ping results from Chaska Network Core: </b><br />")
    print("  Server IP: " + server_ip2 + "<br />")
    print("  Response" + ping2.splitlines()[2].split()[-2] + "ms" + "<br />")
    print ("  " + ping2.splitlines()[-2] + "<br />")
    # Use traceroute to find last hop before server, confirm it's the same from both DCs
    trace1 = net_connect1.send_command("traceroute " + server_ip1)
    #get access switch names from traceroute
    access1 = util.acc_sw(trace1)
    #infer second switch name from first
    access2 = util.acc_pair(access1)

    print("<br />")
    print("Last Layer 3 hop to server found on: <b>" + access1 + "</b><br />")
    print("This switch has a redundant partner: " + access2 + "<br />")
    print("<br />") 
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
        print ("Device MAC Address is: <b>" + mac + "</b><br />")
        print("<br />")
    else:
        print ("MAC Address on " + access1 + ": " + mac1 + "<br />")
        print ("MAC Address on " + access2 + ": " + mac2 + "<br />")
        print("<br />")
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
            print (access1 + " relevant port: " + mac1port + "<br />")
            print ("  " + portdesc1 + "<br />")
            if "down" in (show_pc_1):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE DOWN!" + "</b><br />")
                print(show_pc_1)
                print ("<br />")
            else:
                print("<b>  All members of " + mac1port + " are UP!" + "</b><br />")  
                print("<br />")
                print("  Port Statistics:" + "<br />")
            #function to gather list of port-channel members
            pc_members = util.pc_members_nxos(show_pc_1)
            for member in pc_members:               
                print ("  " + member + "<br />")
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|iscard|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[5].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[7].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil + "<br />")
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
                        print ("    Found: " + error + "<br />")
                if not errors_true:
                    print("    No errors found!" + "<br />") 
        else:
            hostport1 = net_connect3.send_command("show int " + mac1port)
            print ("  " + portdesc1 + "<br />")
            print (hostport1 + "<br />")
        print("<br />")
#needs code to capture and analyze errors on a single-port connection
         
        if "Po" in mac2port:
            pc2_members = []
            show_pc_2 = net_connect4.send_command("show port-channel data int " + mac2port + " | b Ports")
            print (access2 + " relevant port: " + mac2port + "<br />")
            print ("  " + portdesc2 + "<br />")    
            if "down" in (show_pc_2):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE DOWN!" + "</b><br />")
                print(show_pc_2 + "<br />")
            else:
                print("<b>  All members of " + mac2port + " are UP!" + "</b><br />")
                print("<br />")
                print("  Port Statistics:" + "<br />")
            #function to gather list of port-channel members
            pc_members = util.pc_members_nxos(show_pc_2)
            for member in pc_members:                
                print ("  " + member + "<br />")
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|iscard|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[5].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[7].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil + "<br />")
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
                        print ("    Found: " + error + "<br />")
                if not errors_true:
                    print("    No errors found!" + "<br />")                       
        else:
            hostport2 = net_connect4.send_command("show int " + mac2port)
            print ("  " + portdesc2 + "<br />")  
            print (hostport2 + "<br />")
        print("<br />")
#needs code to capture and analyze errors on a single-port connection
 

    else:
    #analyze port-channel statistics for ios
        if "Po" in mac1port:
            show_pc_1 = net_connect3.send_command("show etherchannel " + mac1port[2:] + " summ | i " + mac1port)
            print (access1 + " relevant port: " + mac1port + "<br />")
            print ("  " + portdesc1 + "<br />")
            if "(D)" in (show_pc_1):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE DOWN!" + "</b><br />")
                print(show_pc_1 + "<br />")
            if "(s)" in (show_pc_1):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac1port + " ARE SUSPENDED!" + "</b><br />")
                print(show_pc_1 + "<br />")                
            else:
                print("<b>  All members of " + mac1port + " are UP!" + "</b><br />")  
                print("<br />")
                print("  Port Statistics:" + "<br />")
            #function to gather list of etherchannel members
            pc_members = util.pc_members_ios(show_pc_1)
            for member in pc_members:
                print ("  " + member + "<br />")
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|drop|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[8].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[10].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil + "<br />")
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
            print ("  " + portdesc1 + "<br />")
            print (hostport1 + "<br />")
        print("<br />")
#needs code to capture and analyze errors on a single-port connection
 
            
        if "Po" in mac2port:
            show_pc_2 = net_connect3.send_command("show etherchannel " + mac2port[2:] + " summ | i " + mac2port)
            print (access2 + " relevant port: " + mac2port + "<br />")
            print ("  " + portdesc2 + "<br />")
            if "(D)" in (show_pc_2):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE DOWN!" + "</b><br />")
                print(show_pc_2 + "<br />")
            if "(s)" in (show_pc_2):
                print("<b>FOUND MEMBERS OF PORT-CHANNEL" + mac2port + " ARE SUSPENDED!" + "</b><br />")
                print(show_pc_2 + "<br />")                
            else:
                print("<b>  All members of " + mac2port + " are UP!" + "</b><br />")  
                print("<br />")
                print("  Port Statistics:" + "<br />")
            #function to gather list of etherchannel members
            pc_members = util.pc_members_ios(show_pc_2)
            for member in pc_members:                
                print ("  " + member + "<br />")
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|drop|error")

#needs multi output function for txutil/rxutil formatted in percentage

                txutil = show_int_stats.splitlines()[0].split(' ')[8].split('/')[0]
                rxutil = show_int_stats.splitlines()[0].split(' ')[10].split('/')[0]
                txutil = ("{0:.0%}".format(int(txutil)/255))
                rxutil = ("{0:.0%}".format(int(rxutil)/255))
                print ("    Transmit utilization: " + txutil + "  Receive utilization: " + rxutil + "<br />")
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
                    print("    No errors found!" + "<br />")
                else:
                    for error in errors_true:
                        print ("    Found: " + error + "<br />")
        else:
            hostport2 = net_connect4.send_command("show int " + mac2port)
            print ("  " + portdesc2 + "<br />")
            print (hostport2 + "<br />")
        print("<br />")
#needs code to capture and analyze errors on a single-port connection
 

except:
    print ("An exception occurred with access network analysis!, program exiting")   

finally:    
    #close out the access switch connections
    net_connect3.disconnect()
    net_connect4.disconnect()
print ("Job Complete")
