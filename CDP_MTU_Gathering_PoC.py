# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:31:29 2020

@author: gnasses
"""
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import re
import util
from netmiko import Netmiko
from ntc_templates.parse import parse_output
# Init app
app = Flask(__name__)
# Database
"""
To build/rebuild a db, execute the following after stopping the app, closing the python console and deleting the old .db file:
from app import db
db.create_all()
"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MTU.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)
# BGP Database Class/Model
class MTU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(100), nullable=False)
    destination_host = db.Column(db.String(100), nullable=False)
    local_port = db.Column(db.String(40))
    management_ip = db.Column(db.String(15))
    mtu = db.Column(db.String(10))
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        device = request.form['device']
        mtus = MTU.query.filter(MTU.device == device).all()
        return render_template('mtu_index.html', mtus=mtus)
    else:
        mtus = MTU.query.order_by(MTU.id).all() 
        return render_template('mtu_index.html', mtus=mtus) 
@app.route('/refresh', methods=['POST', 'GET'])
def refresh():
    devices = ['mls_starting_switch'] 
    db.session.query(MTU).delete()
    db.session.commit()
    while len(devices) >= 1:
        device = devices[0]
        print ("Device = " + device) 
        try:
            switch = util.CiscoDeviceRO(host=device)
            net_connect = Netmiko(**switch.__dict__)
            cdp_raw = net_connect.send_command("show cdp neighbor detail")
            sw_ver = util.nxos_check(device)
            if sw_ver == 'nxos':
                cdp_parsed = parse_output(platform="cisco_nxos", command="show cdp neighbor detail", data=cdp_raw)
            else:
                cdp_parsed = parse_output(platform="cisco_ios", command="show cdp neighbor detail", data=cdp_raw)
#            print (cdp_parsed)
            for sub in cdp_parsed:
                if sw_ver == "nxos": 
                    destination_host = sub['dest_host'].split('.')[0].split('-')[0].split('(')[0].lower()
                    management_ip = sub['mgmt_ip']
                    local_port = sub['local_port']
                else:    
                    destination_host = sub['destination_host'].split('.')[0].split('-')[0].split('(')[0].lower()
                    management_ip = sub['management_ip']
                    local_port = sub['local_port']                          
                if "mls" in destination_host:
                    try:
                        mtu_raw = net_connect.send_command("show interface " + local_port + " | include MTU")
                        m = re.search('MTU\s\d+', mtu_raw)
                        mtu = m.group(0)
                    except:
                        mtu = "Error finding MTU" 
                    print("Entry: " + destination_host, management_ip, local_port, mtu)
                    known_device = []
                    known_device = MTU.query.filter(MTU.device == destination_host).all()
                    if not known_device:
                        if destination_host not in devices:
                            devices.append(destination_host)                   
                    print ("# of devices: " + str(len(devices)))
                    new_mtu = MTU(device=device, destination_host=destination_host, local_port=local_port, management_ip=management_ip, mtu=mtu)
                    try:
                        db.session.add(new_mtu)
                        db.session.commit() 
                    except:
                        print ("could not add cdp entry")
        except: 
            print("Could not connect to this device")
        finally:
            try:
                net_connect.disconnect()
            except:
                print ("no connection to disconnect")
        devices.remove(device)
    mtus = MTU.query.order_by(MTU.id).all()       
    return render_template('mtu_index.html', mtus=mtus)
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5019)
