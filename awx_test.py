# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:32:04 2019

@author: gnasses

AWX API testing script

"""
import sys, os.path, datetime
import urllib, json, base64
import requests, json
# Ansible tower_cli python libs
import tower_cli
import ansible

response = requests.get("http://192.168.1.1/api/login/")

job = requests.post("http://192.168.1.1/api/v2/job_templates/169/launch/")
