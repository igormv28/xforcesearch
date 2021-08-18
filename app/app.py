from flask import Flask, g, redirect, url_for, request, render_template, Response, session, make_response
from werkzeug.wrappers import CommonResponseDescriptorsMixin
from flask_oidc import OpenIDConnect
import uuid
import os
import re
import json
import requests
from urllib.request import urlopen
from datetime import datetime

def _force_https(wsgi_app):
    def wrapper(environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return wsgi_app(environ, start_response)
    return wrapper
app = Flask(__name__)
with open('artifact/w3id_sso.json') as f:
    w3id_sso_json = json.load(f)
w3id_sso_json["web"]["client_id"] = os.environ.get("OIDC_CLIENTID")
w3id_sso_json["web"]["client_secret"] = os.environ.get("OIDC_CLIENTSECRET")
OIDC_SECRETKEY = os.environ.get("OIDC_SECRETKEY")
OIDC_SECRETKEY_VAL = str(OIDC_SECRETKEY).encode('ISO-8859-1').decode('unicode-escape')
OIDC_USERNAME = os.environ.get("OIDC_USERNAME")
OIDC_TOKEN = os.environ.get("OIDC_TOKEN")
ephefile = uuid.uuid4().hex
with open(ephefile, 'w') as json_file:
    json.dump(w3id_sso_json, json_file)
app.wsgi_app = _force_https(app.wsgi_app)
app.config["OIDC_CLIENT_SECRETS"] = ephefile
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
app.config["SECRET_KEY"] = OIDC_SECRETKEY_VAL
oidc = OpenIDConnect(app) 
os.remove(ephefile)
responsemd5 = uuid.uuid4().hex

@app.after_request
def add_header(response):
    response.headers['cache-control'] = 'private, no-cache, no-store, must-revalidate; Secure; HttpOnly'
    response.set_cookie('biscoito', '3', max_age=600)
    response.headers['server'] = 'STOP! This is a browser feature intended for developers. If you re-use something from here to enable a XFS feature or "hack" without notifying a "pentesting", it is NOT nice and will record your steps.'
    response.headers['content-security-policy'] = "default-src * 'self' blob: *.ibm.com 'unsafe-inline'; script-src *.ibm.com 'unsafe-inline';connect-src *.ibm.com blob: *.ibmcloud.com 'self'; frame-src * 'self' data: blob: *.ibm.com 'unsafe-inline' 'unsafe-eval' ; object-src 'none'; block-all-mixed-content; upgrade-insecure-requests; frame-ancestors 'self'"
    response.headers['access-control-allow-headers'] = 'x-csrf-token'
    response.headers['x-xss-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['access-control-allow-origin'] = 'https://xforcesearch.c8f8f055.public.multi-containers.ibm.com/'
    response.headers['access-control-allow-credentials'] = 'true'
    response.headers['strict-transport-security'] = 'max-age=31536000; includeSubDomains'
    response.headers['x-content-type-options'] = 'nosniff'
    return response

@app.route('/',methods = ['POST', 'GET'])
@oidc.require_login
def search():
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    sessionmd5 = uuid.uuid4().hex
    cveid = 'https://api.xforce.ibmcloud.com/vulnerabilities/search/'
    prodname = 'https://api.xforce.ibmcloud.com/vulnerabilities/fulltext?q=platforms_affected:'
    try:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            print(" HTTP request from IP: ", request.environ['REMOTE_ADDR'], "\n")
        else:
            print(" HTTP request from IP: ", request.environ['HTTP_X_FORWARDED_FOR'], "\n")
    except KeyError as ipwho:
        print(" IP not informed: ", ipwho)
    if request.method == 'POST':
        platform = request.form['platform']
        version = request.form['version']
        if platform == "":
            pass
        else:
            print("Query sent: ", platform)
        if version == "":
            pass
        else:
            print(version)
        object_list = []
        matched_CVE_list = []  
        if str(platform).find("CVE-") == 0:
            stdcode = platform
            stdclr = re.sub(r'[^A-Za-z0-9-. ]+', '', stdcode)
            print("Query processed: ", stdclr)
            url = cveid + str(stdclr)
            response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
            resjson = json.loads(response.content)
            if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                for i in resjson:
                    if i["stdcode"][0] == stdcode:
                        object_list.append(i)
            else:
                object_list = [] 
        else:
            platclr = re.sub(r'[^A-Za-z0-9. ]+', '', platform)
            print("Query processed: ", platclr)
            url = prodname + '"' + platclr + '"'
            response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
            resjson = json.loads(response.content)
            if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                object_list = resjson["rows"]
            else:
                object_list = []
        contentmd5 = uuid.uuid4().hex
        renderpg = make_response(render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, arr_platform=''))
        renderpg.headers.set('content-md5', contentmd5)
        return renderpg

    else:
        arr_platforms = []
        text_file = open("artifact/platforms.txt", "r", encoding='ISO-8859-1')
        arr_platforms = text_file.readlines()
        contentmd5 = uuid.uuid4().hex
        renderpg = make_response(render_template('search.html', arr_platform = '___'.join(arr_platforms)))
        renderpg.headers.set('content-md5', contentmd5)
        return renderpg
app.run(host='0.0.0.0',port=8080, debug = True, use_reloader = False)
