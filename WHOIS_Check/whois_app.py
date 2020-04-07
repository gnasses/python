from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from netmiko import Netmiko
import util
import json
import subprocess
from ntc_templates.parse import parse_output
from pythonping import ping
# Init app
app = Flask(__name__)
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpwd@localhost:3306/whois'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)
#Whois Database Class/Mode
class WHOIS(db.Model):
    ip = db.Column(db.String(20), primary_key=True)
    route = db.Column(db.String(20))
    as_number = db.Column(db.String(10))
    provider = db.Column(db.String(25))
    country = db.Column(db.String(25))

    def __repr__(self):
        return '<%r>' % self.ip
# WHOIS Schema for Marshmallow API Functionality
class WHOISSchema(ma.Schema):
    class Meta:
        fields = ('ip', 'route', 'as_number', 'provider', 'country')
# Init Schema        
WHOIS_schema = WHOISSchema()
WHOISs_schema = WHOISSchema(many=True)
"""
To build/rebuild a db, execute the following after stopping the app, closing the python console and deleting the old .db file:
from app import db
db.create_all()
"""
#App Routes
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        asnip = request.form['asnip']
        q = WHOIS.query.filter(WHOIS.ip.contains(asnip)).first()
        if q:
            db.session.delete(q)
            db.session.commit()   
        command = ("/usr/bin/whois")
        out = subprocess.Popen([command, '-h', 'whois.cymru.com', '-v', asnip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        s = str(stdout.splitlines()[2])
        l = (s[2:-1])
        ip =  l.split('|')[1][1:16]
        route = l.split('|')[2][1:19]
        as_number = l.split('|')[0][0:4]
        provider = l.split('|')[6][1:]
        country = l.split('|')[3][1:3]
        new_whois = WHOIS(ip=ip, route=route, as_number=as_number, provider=provider, country=country)
        try:
            db.session.add(new_whois)
            db.session.commit()
        except:
            return 'There was an issue checking WHOIS for this IP, it may already exist in the Database'
        whois = WHOIS.query.filter(WHOIS.ip == ip).all()
        return render_template('index.html', whois=whois)
    else:
        whois = WHOIS.query.order_by(WHOIS.ip).all()
        return render_template('index.html', whois=whois)
@app.route('/clear', methods=['POST', 'GET'])
def clearout():
    query = db.session.query(WHOIS).delete()
    db.session.commit()
    return redirect('/')

#API Routes
#API Add to db
@app.route('/api/<address>', methods=['POST'])
def add_whois(address):
    asnip = address
    q = WHOIS.query.filter(WHOIS.ip.contains(asnip)).first()
    if q:
        db.session.delete(q)
        db.session.commit()     
    command = ("/usr/bin/whois")
    out = subprocess.Popen([command, '-h', 'whois.cymru.com', '-v', asnip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    s = str(stdout.splitlines()[2])
    l = (s[2:-1])
    ip =  l.split('|')[1][1:16]
    route = l.split('|')[2][1:19]
    as_number = l.split('|')[0][0:4]
    provider = l.split('|')[6][1:]
    country = l.split('|')[3][1:3]
    new_whois = WHOIS(ip=ip, route=route, as_number=as_number, provider=provider, country=country)
    try:
        db.session.add(new_whois)
        db.session.commit()
    except:
        return 'There was an issue checking WHOIS for this IP'
    return WHOIS_schema.jsonify(new_whois)

# API Delete Entry
@app.route('/api/<ip>', methods = ['DELETE'])
def delete_whois(ip):
    asnip = WHOIS.query.get(ip)
    db.session.delete(ip)
    db.session.commit()
    return WHOIS_schema.jsonify(asnip)

# Run App 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5016, debug=True)
© 2020 GitHub, Inc.
