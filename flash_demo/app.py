# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 21:50:56 2019

@author: gnasses
"""

from __future__ import print_function, unicode_literals
from flask import Flask, render_template, request
import cgi
from wsgiref.handlers import CGIHandler
#from flask_sqlalchemy import SQLalchemy
#from datetime import datetime
#from netmiko import Netmiko
#import sys
#import os.path
#import util
#import nxapicheck
#import vulncheck_cfs


app = Flask(__name__)
title = ("Results page")   

app1 = Flask(__name__)
title = ("Cisco NX-API Vulnerabilities (NXOS)")  

app2 = Flask(__name__)
title = ("Cisco Fabric Services Vulnerabilities (NXOS)")     

app3 = Flask(__name__)
title = ("TVM Script Execution")    

app4 = Flask(__name__)
title = ("Sorted Vulnerability List") 
#app4 = Flask(__name__)
#title = ("Button 1 execute")  
#
#app5 = Flask(__name__)
#title = ("Button 2 execute")
#
#app6 = Flask(__name__)
#title = ("Server Validation Form") 

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/results')
def run_app():
    return render_template('results.html')

@app.route('/vuln0065517')
def run_app1():
    return render_template('vuln0065517.html')
    
@app.route('/vuln0065238')
def run_app2():
    return render_template('vuln0065238.html')

@app.route('/tvm', methods=['POST', 'GET'])
def run_app3():
    if request.method == 'POST':
        return render_template('tvmresults.html')
    else:    
        return render_template('tvm.html')

@app.route('/vulncount')
def run_app4():
    return render_template('vulncount.html')    
  
#@app.route('/run_vuln0065517', methods=['POST', 'GET'])
#def run_app4():
#    if request.method == 'POST':
#        pass
#    else:
#        return "Manual Script Generation Underway, this will take some time. Check the Results after 1 hour."
#        #nxapicheck()
#
#@app.route('/run_vuln0065238', methods=['POST', 'GET'])
#def run_app5():
#    if request.method == 'POST':
#        pass
#    else:
#        return "Manual Script Generation Underway, this will take some time. Check the Results after 1 hour."
##        vulncheck_cfs()
#
#@app.route('/run_validation', methods=['POST', 'GET'])
#def run_app6():
#    if request.method == 'POST':
#        hostname = request.form['content']
#        servervalidation_form.validate(hostname)
#        return render_template('complete.html')
#    else: 
#        return render_template('validation.html')
    
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    
