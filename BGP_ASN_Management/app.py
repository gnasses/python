from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from netmiko import Netmiko
import util
import json
from ntc_templates.parse import parse_output
# Init app
app = Flask(__name__)
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bgp_asn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)
# BGP Database Class/Model
class BGP(db.Model):
    number = db.Column(db.String(5), nullable=False, primary_key=True)
    desc = db.Column(db.String(140), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<%r>' % self.number
# BGP Schema for Marshmallow API Functionality
class BGPSchema(ma.Schema):
    class Meta:
        fields = ('number', 'desc', 'date_created')
# Init Schema
BGP_schema = BGPSchema()
BGPs_schema = BGPSchema(many=True)           
"""
To build/rebuild a db, execute the following after stopping the app, closing the python console and deleting the old .db file:
from app import db
db.create_all()
"""
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        asn_number = request.form['number']
        asn_desc = request.form['desc']
        new_asn = BGP(number=asn_number, desc=asn_desc)
        if int(asn_number) >= 64512 and int(asn_number) <= 65535: 
            try:
                db.session.add(new_asn)
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue adding your ASN, it probably already exists in Database'
        else:
            return 'ASN out of Range'
    else:
        asns = BGP.query.order_by(BGP.number).all()
        used = len(asns)
        util = ("{0:.0%}".format(int(used)/1024))
        return render_template('index.html', asns=asns, used=used, util=util)

@app.route('/delete/<string:number>')
def delete(number):
    asn_to_delete = BGP.query.get_or_404(number)

    try:
        db.session.delete(asn_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that ASN'

@app.route('/update/<string:number>', methods=['GET', 'POST'])
def update(number):
    asn = BGP.query.get_or_404(number)
    if request.method == 'POST':
        asn.number = request.form['number']
        asn.desc = request.form['desc']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your asn'

    else:
        return render_template('update.html', asn=asn)

@app.route('/import/', methods=['POST', 'GET'])
def import_asns():
    if request.method == 'GET':
        devices = ['DC1-coresw', 'DC2-coresw', 'DC3-coresw']
        aslist = []
        for dev in devices:
            device = util.CiscoDeviceRO(host=dev)
            dev_connect = Netmiko(**device.__dict__)
            bgp_out = dev_connect.send_command("show ip bgp vrf all all")
            bgp_parsed = parse_output(platform="cisco_nxos", command="show ip bgp", data=bgp_out)
            dev_connect.disconnect()
            print ("Collected BGP table for " + dev)
            print ('<br />')
            bgpasns = [ sub['as_path'] for sub in bgp_parsed ]
            for asn in bgpasns:
                asnsplit = asn.split()
                for asnum in asnsplit:
                    if asnum not in aslist and int(asnum) >=64512 and int(asnum) <=65535:
                        aslist.append(asnum)
        as_map = map(int, aslist)
        as_sort = sorted(as_map)
        for sort in as_sort:
            asn_status = BGP.query.get(sort)
            if asn_status == None:
                new_asn = BGP(number=sort, desc='Imported from Core BGP Table')
                try:
                    db.session.add(new_asn)
                    db.session.commit()
                except:  
                    continue
        return redirect('/')        

@app.route('/query', methods=['GET', 'POST'])
def top5():
    bgpnext = []
    avail = 64512
    avail_count = 5
    while avail_count > 0:
        result = BGP.query.get(avail)
        if result is None:
            bgpnext.append(avail)
            avail_count = avail_count -1
        else:
            print ('ASN used')
        avail = avail +1        
    return render_template('query.html', bgpnext=bgpnext)

# API Routes
# API Create ASN
@app.route('/api', methods = ['POST'])
def add_asn():
    asn_number = request.json['number']
    asn_desc = request.json['desc']
    new_asn = BGP(number=asn_number, desc=asn_desc)
    if int(asn_number) >= 64512 and int(asn_number) <= 65535:
        db.session.add(new_asn)
        db.session.commit()
        return BGP_schema.jsonify(new_asn)
    else:
        return {"message": "Requested ASN is outside of Private Range (64512 - 65535) "}, 403
# API Get ASN
@app.route('/api/<number>', methods = ['GET'])
def get_asn(number):
    asn = BGP.query.get(number)
    return BGP_schema.jsonify(asn) 
# API Get All ASNs
@app.route('/api', methods = ['GET'])
def get_all_asns():
    asns = BGP.query.order_by(BGP.number).all()
    result = BGPs_schema.dump(asns)
    return jsonify(result)
# API Update ASN
@app.route('/api/<number>', methods = ['PUT'])
def update_asn(number):
    asn = BGP.query.get(number)
    asn_desc = request.json['desc']
    asn.desc = asn_desc
    db.session.commit()
    return BGP_schema.jsonify(asn)
# API Delete ASN
@app.route('/api/<number>', methods = ['DELETE'])
def delete_asn(number):
    asn = BGP.query.get(number)
    db.session.delete(asn)
    db.session.commit()
    return BGP_schema.jsonify(asn)
#API Single Query
@app.route('/api/querynext', methods=['GET'])
def avail_asn():
    avail = 64512
    avail_count = 1
    while avail_count > 0:
        result = BGP.query.get(avail)
        if result is None:
            avail_count = avail_count -1
            return json.dumps(avail)
        avail = avail +1   


# Run App 
if __name__ == "__main__":
    app.run(host='0.0.0.0')
