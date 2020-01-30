#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import datetime
import time
from netmiko import Netmiko
import util
import cgi
import cgitb
cgitb.enable()
form = cgi.FieldStorage()
hostname = form.getfirst('content2')
print("Content-Type: text/html\n\n")
print('''
<style>
table {
  border-collapse: collapse;
}

td, th {
  border: 1px solid black;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>''')
now = str(datetime.datetime.now())
try:
    mlselr01ebr01 = util.CiscoDeviceRO(host="mlselr01ebr01")
    mlsctc01ebr01 = util.CiscoDeviceRO(host="mlsctc01ebr01")
    ping1 = ()
    while len(ping1) <= 50:
        net_connect1 = Netmiko(**mlselr01ebr01.__dict__)
        net_connect2 = Netmiko(**mlsctc01ebr01.__dict__)
        ping1 = net_connect1.send_command("ping " + hostname + " count 100")
        ping2 = net_connect2.send_command("ping " + hostname + " count 100")
        if len(ping1) <= 50: 
            print ("Could not resolve servername. Please try again.")
        else:
            print('<br />')        
    server_ip1 = ping1.splitlines()[2].split()[3][:-1]
    server_ip2 = ping2.splitlines()[2].split()[3][:-1]
    trace1 = net_connect1.send_command("traceroute " + server_ip1)
    access1 = util.acc_sw(trace1)
    access2 = util.acc_pair(access1)
except:
    print ("An exception occurred in ping testing from Core network, program exiting")
    exit()
finally:
    net_connect1.disconnect()
    net_connect2.disconnect()
    
try:
    my_device3 = util.CiscoDeviceRO(host=access1)
    my_device4 = util.CiscoDeviceRO(host=access2)
    net_connect3 = Netmiko(**my_device3.__dict__)
    net_connect4 = Netmiko(**my_device4.__dict__)
    #determine OS_Type
    nxos_check = net_connect3.send_command("show version")
    if "NX-OS" in nxos_check:
        sw_ver = "nxos"
    else:
        sw_ver = "ios"
    ping3 = net_connect3.send_command("ping " + server_ip1)
    ping4 = net_connect4.send_command("ping " + server_ip1)
    arp1 = net_connect3.send_command("show ip arp " + server_ip1)
    arp2 = net_connect4.send_command("show ip arp " + server_ip1)
    if sw_ver == "nxos":
        mac1 = arp1.splitlines()[-1].split()[2]
        mac2 = arp2.splitlines()[-1].split()[2]
    else: 
        mac1 = arp1.splitlines()[-1].split()[3]
        mac2 = arp2.splitlines()[-1].split()[3]
    #check if same MAC seen from both switches
    if mac1 == mac2:
        mac = mac1
    else:
        mac = ("Access Switch MACs do not match" + mac1 + "&" + mac2)
    #find port the server MAC connects to
    show_mac_1 = net_connect3.send_command("show mac addr addr " + mac1)
    show_mac_2 = net_connect4.send_command("show mac addr addr " + mac2)
    mac1port = show_mac_1.splitlines()[-1].split()[-1]
    mac2port = show_mac_2.splitlines()[-1].split()[-1]
    #capture the port description
    portdesc1 = net_connect3.send_command("show interface description | i " + mac1port)
    portdesc2 = net_connect4.send_command("show interface description | i " + mac2port)
    if "Po" in mac1port:
        if sw_ver == "nxos": 
            show_pc_1 = net_connect3.send_command("show port-channel data int " + mac1port + " | b Ports")
            pc1_members = util.pc_members_nxos(show_pc_1)
        else: 
            show_pc_1 = net_connect3.send_command("show etherchannel " + mac1port[2:] + " summ | i " + mac1port)
            pc1_members = util.pc_members_ios(show_pc_1)
    else:
        pc1_members = []
        pc1_members.append(mac1port)
#    print (pc1_members)        
    if "Po" in mac2port:
        if sw_ver == "nxos": 
            show_pc_2 = net_connect4.send_command("show port-channel data int " + mac2port + " | b Ports")
            pc2_members = util.pc_members_nxos(show_pc_2)
        else:
            show_pc_2 = net_connect4.send_command("show etherchannel " + mac2port[2:] + " summ | i " + mac2port)
            pc2_members = util.pc_members_ios(show_pc_2)
    else:
        pc2_members = []
        pc2_members.append(mac2port)
#    print (pc2_members)
    table_report='''<h2> Detailed Port Error Checking Report</h2>
    <table>
      <caption><b>Host Testing Details</b></caption>
      <tr>
        <td><b>Report Date/Time</b></td>
        <td> {0}  </td>
      </tr>
      <tr>
        <td><b>Hostname</b></td>
        <td> {1} </td>
      </tr>
      <tr>
        <td><b>IP Address</b></td>
        <td> {2} </td>
      </tr>
      <tr>
        <td><b>Host MAC Address<b></td>
        <td> {3} </td>
      </tr>
    </table> <br />'''
    print (table_report.format(now.split('.')[0], hostname,  server_ip1, mac))        
    tabledata = []
    iter = 5
    while iter > 0:
        for member in pc1_members:            
            if sw_ver == "nxos":
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|iscard|error")
                errors_true = util.err_true_nxos(show_int_stats)
            else: 
                show_int_stats = net_connect3.send_command("show int " + member + " | i reliability|drops|error")
                errors_true = util.err_true_ios(show_int_stats)
#            print (errors_true)
            data = []
            data.append(member) 
            data.append(errors_true)
            tabledata.append(data)
#        print (tabledata)
        time.sleep(45)
        iter = (iter-1)
    if net_connect3: net_connect3.disconnect()
    print ("<table><caption><b>" + access1 + "</b></caption><tr><th>Port</th><th>Beginning Error Count</th><th>After 1 min</th><th>After 2mins</th><th>After 3mins</th><th>After 4 mins</th></tr>")
    ml1 = (len(pc1_members))
    tlen = ml1
    tlen = (tlen-1)
    while tlen >= 0:
        f1 = str(tabledata[tlen][0])
        f2 = str(tabledata[tlen][1:])
        f3 = str(tabledata[tlen + ml1][1])
        f4 = str(tabledata[tlen + (2 * ml1)][1:])
        f5 = str(tabledata[tlen + (3 * ml1)][1:])
        f6 = str(tabledata[tlen + (4 * ml1)][1:])
        print("<tr><td><b>" + f1 + "</b></td><td>" + f2[2:-2] + "</td><td>" + f3[2:-2] + "</td><td>" + f4[2:-2] + "</td><td>" + f5[2:-2] + "</td><td>" + f6[1:-1] + "</td></tr>")
        tlen = (tlen-1)
    print ("</table><br /><br />")  
      
    tabledata2 = []
    iter = 5
    while iter > 0:
        for member in pc2_members:            
            if sw_ver == "nxos":
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|iscard|error")
                errors_true = util.err_true_nxos(show_int_stats)
            else:
                show_int_stats = net_connect4.send_command("show int " + member + " | i reliability|drops|error")
                errors_true = util.err_true_ios(show_int_stats)
 #           print (errors_true)
            data = []
            data.append(member) 
            data.append(errors_true)
            tabledata2.append(data)
#        print (tabledata2)
        time.sleep(45)
        iter = (iter-1)
    if net_connect4: net_connect4.disconnect()
    print ("<table><caption><b>" + access2 + "</b></caption><tr><th>Port</th><th>Beginning Error Count</th><th>After 1 min</th><th>After 2mins</th><th>After 3mins</th><th>After 4mins</th></tr>")
    ml1 = (len(pc2_members))
    tlen = ml1
    tlen = (tlen-1)
    while tlen >= 0:
        f1 = str(tabledata2[tlen][0])
        f2 = str(tabledata2[tlen][1:])
        f3 = str(tabledata2[tlen + ml1][1:])
        f4 = str(tabledata2[tlen + (2 * ml1)][1:])
        f5 = str(tabledata2[tlen + (3 * ml1)][1:])
        f6 = str(tabledata2[tlen + (4 * ml1)][1:])
        print("<tr><td><b>" + f1 + "</b></td><td>" + f2[2:-2] + "</td><td>" + f3[2:-2] + "</td><td>" + f4[2:-2] + "</td><td>" + f5[2:-2] + "</td><td>" + f6[2:-2] + "</td></tr>")
        tlen = (tlen-1)
    print ("</table><br /><br />") 
except:
    print ("An exception occurred with access network analysis!, program exiting")   

finally:    
    #close out the access switch connections
    if net_connect3: net_connect3.disconnect()
    if net_connect4: net_connect4.disconnect()
print ("Job Complete")
