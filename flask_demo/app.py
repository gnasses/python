from __future__ import print_function, unicode_literals
from flask import Flask, render_template, request
import cgi
from wsgiref.handlers import CGIHandler

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


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
#    return "Hello WSGI Drinkers!"
# above simple return for testing

@app.route('/results')
def run_app():
    return render_template('results.html')
#    return "Hello WSGI Drinkers!"
# above simple return for testing

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


if __name__ == '__main__':
  app.run(host='10.1.1.1', debug=True)
