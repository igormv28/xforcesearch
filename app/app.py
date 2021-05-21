from flask import Flask, g, redirect, url_for, request, render_template, Response, session, make_response
from flask_oidc import OpenIDConnect
import uuid
import os
import json
import requests
from datetime import datetime
from urllib.request import urlopen
import math

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
with open('temp.json', 'w') as json_file:
    json.dump(w3id_sso_json, json_file)
app.wsgi_app = _force_https(app.wsgi_app)
app.config["OIDC_CLIENT_SECRETS"] = "temp.json"
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
app.config["SECRET_KEY"] = OIDC_SECRETKEY_VAL
oidc = OpenIDConnect(app)
os.remove("temp.json")
@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.set_cookie('biscoito', '3', max_age=600)
    response.headers['server'] = 'OpenShift'
    response.headers['access-control-allow-origin'] = 'https://xforcesearch.wdc1a.ciocloud.nonprod.intranet.ibm.com/'
    response.headers['access-control-allow-credentials'] = 'true'
    response.headers['access-control-allow-headers'] = 'x-csrf-token'
    return response
@app.route('/',methods = ['POST', 'GET'])
@oidc.require_login
def search():
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    firstname = g.oidc_id_token['firstName']
    bluegroup = g.oidc_id_token['blueGroups']
    email = g.oidc_id_token['email']
    logfile = "users.log"
    if request.method == 'POST':
        platform = request.form['platform']
        version = request.form['version']
        if platform == "":
            print("platform none")
        else:
            print(platform)
        if version == "":
            print("version none")
        else:
            print(version)
        object_list = []
        matched_CVE_list = []  
        if version == "" and platform != "":
            if (os.path.isfile(logfile)):
                wait = 0
                nowdt = datetime.now().timestamp()
                f = open(logfile, "r")
                for x in f:
                    dt = float(str(str(x).split("   ")[1]).replace("\n", ""))
                    # Get wait time for user
                    if str(x).find(firstname) > -1:
                        if dt > nowdt:
                            wait = math.ceil((dt - nowdt) / 60)
                            print(wait)
                # Founded future time (disabled wait time)
                if wait > 0:
                    print("Already disabled - 1")
                    return render_template('search.html', result = [], platform = "", version = "", foundresult = [], email = email, bluegroup = bluegroup, firstname = firstname, wait = wait, arr_platform='')
                else:
                    if str(platform).find("CVE-") == 0:
                        stdcode = platform
                        url = 'https://api.xforce.ibmcloud.com/vulnerabilities/search/' + str(stdcode).replace("'","")
                        print(url)
                        response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
                        #respcont = response.content
                       # resjson = json.dumps(respcont.decode("utf-8"))
                        resjson = json.loads(response.content)
                        #print (json.dumps(resjson, indent=4, sort_keys=True))
                        if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                            for i in resjson:
                                if i["stdcode"][0] == stdcode:
                                    object_list.append(i)
                        else:
                            object_list = [] 
                    else:
                        url = 'https://api.xforce.ibmcloud.com/vulnerabilities/fulltext?q=platforms_affected:"' + platform.replace("'","") + '"'
                        response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
                        resjson = json.loads(response.content)
                        print(url)
                        if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                            object_list = resjson["rows"]
                        else:
                            object_list = []
                    return render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform='')
            else:
                if str(platform).find("CVE-") == 0:
                    stdcode = platform
                    url = 'https://api.xforce.ibmcloud.com/vulnerabilities/search/' + str(stdcode).replace("'","")
                    print(url)
                    response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
                    resjson = json.loads(response.content)
                    #print (json.dumps(resjson, indent=4, sort_keys=True))
                    if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                        for i in resjson:
                            if i["stdcode"][0] == stdcode:
                                object_list.append(i)
                    else:
                        object_list = [] 
                else:
                    url = 'https://api.xforce.ibmcloud.com/vulnerabilities/fulltext?q=platforms_affected:"' + platform.replace("'","") + '"'
                    response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
                    resjson = json.loads(response.content)
                    if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                        object_list = resjson["rows"]
                    else:
                        object_list = []
                return render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform='')
        # Read user log file
        if (os.path.isfile(logfile)):
            # Find future time for the user
            wait = 0
            recents = []
            timelimit = 3
            disabletime = 30
            nowdt = datetime.now().timestamp()
            f = open(logfile, "r")
            for x in f:
                dt = float(str(str(x).split("   ")[1]).replace("\n", ""))
                # Get the recent users log list
                print("Get the recent list")
                if math.ceil((nowdt - dt) / 60) < timelimit:
                    recents.append(x)
                # Get wait time for user
                if str(x).find(firstname) > -1:
                    if dt > nowdt:
                        wait = math.ceil((dt - nowdt) / 60)
                        print(wait)
            # Founded future time (disabled wait time)
            if wait > 0:
                print("Already disabled - 1")
                return render_template('search.html', result = [], platform = "", version = "", foundresult = [], email = email, bluegroup = bluegroup, firstname = firstname, wait = wait, arr_platform='')
            else:
                # Clean Up
                print("Clean Up")
                if recents != []:
                    f = open(logfile, "w")
                    f.write(''.join(recents))
                    f.close()
                # Get the firstname list
                print("Get the firstname list")
                mylist = []
                for i in recents:
                    if str(i).split("   ")[0] == firstname:
                        mylist.append(i)
                # if mylist count is greater than 2
                if len(mylist) > 0:
                    wait = 0
                    nowdt = datetime.now().timestamp()
                    for x in mylist:
                        dt = float(str(str(x).split("   ")[1]).replace("\n", ""))
                        # Get wait time for user
                        if dt > nowdt:
                            wait = math.floor((dt - nowdt) / 60)
                            print(wait)
                    if wait > 0:
                        print("Already disabled : ", wait)
                        return render_template('search.html', result = [], platform = "", version = "", foundresult = [], email = email, bluegroup = bluegroup, firstname = firstname, wait = wait, arr_platform='')
                    else:
                        if len(mylist) == 2:
                            print("Set disable")
                            f = open(logfile, "a")
                            f.write(firstname + "   " + str(datetime.now().timestamp() + disabletime * 60) + "\n")
                            f.close()
                            return render_template('search.html', result = [], platform = "", version = "", foundresult = [], email = email, bluegroup = bluegroup, firstname = firstname, wait = disabletime, arr_platform='')
                        else:
                            print("Add new line - 0")
                            f = open(logfile, "a")
                            f.write(firstname + "   " + str(datetime.now().timestamp()) + "\n")
                            f.close()
                            # Search
                            object_list, matched_CVE_list, platform, version = doSearch(platform, version)
                            return render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform='')
                else:
                    print("Add new line - 1")
                    f = open(logfile, "a")
                    f.write(firstname + "   " + str(datetime.now().timestamp()) + "\n")
                    f.close()
                    # Search
                    object_list, matched_CVE_list, platform, version = doSearch(platform, version)
                    return render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform='')
        else:
            print("Add new line - 2")
            f = open(logfile, "a")
            f.write(firstname + "   " + str(datetime.now().timestamp()) + "\n")
            f.close()
            # Search
            object_list, matched_CVE_list, platform, version = doSearch(platform, version)        
            return render_template('search.html', result = object_list, platform = platform, version = version, foundresult = matched_CVE_list, email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform='')
    else:
        arr_platforms = []
        text_file = open("artifact/platforms.txt", "r", encoding='ISO-8859-1')
        arr_platforms = text_file.readlines()
        return render_template('search.html', email = email, bluegroup = bluegroup, firstname = firstname, wait = 0, arr_platform = '___'.join(arr_platforms), disablebuild = 'disabled')
def doSearch(platform, version):
    object_list = []
    matched_CVE_list = []
    CVE_list = []
    if version != "" and platform != "":
        starttime = datetime.timestamp(datetime.now())
        if str(platform).find("CVE-") == 0:
            stdcode = platform
            url = 'https://api.xforce.ibmcloud.com/vulnerabilities/search/' + str(stdcode).replace("'","")
            print(url)
            response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
            resjson = json.loads(response.content)
            #print (json.dumps(resjson, indent=4, sort_keys=True))
            if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                for i in resjson:
                    if i["stdcode"][0] == stdcode:
                        object_list.append(i)
                for i in object_list:
                    tmp = []
                    for j in i["references"]:
                        tmp.append(j["link_target"])
                    CVE_list.append(tmp)
                for links in CVE_list:
                    cnt = 0
                    for link in links:
                        print(link)
                        try:
                            fp = urlopen(link, timeout=5)
                            mybytes = fp.read()
                            content = mybytes.decode("utf8")
                            fp.close()
                            found = str(content).find(str(version))
                            if found > -1:
                                matched_CVE_list.append(1)
                                cnt += 1
                                break
                        except:
                            continue
                    founded = "Found"
                    if cnt == 0:
                        matched_CVE_list.append(0)
                        founded = "Not Found"
                    #print(CVE_list.index(links), object_list[CVE_list.index(links)]["stdcode"][0], founded)
                    print("="*50)
                endtime = datetime.timestamp(datetime.now())
                print("Consumed Time : ", endtime - starttime, " Sec")
            else:
                object_list = []
                matched_CVE_list = []
        else:
            url = 'https://api.xforce.ibmcloud.com/vulnerabilities/fulltext?q=platforms_affected:"' + platform.replace("'","") + '"'
            response = requests.get(url, auth=(OIDC_USERNAME, OIDC_TOKEN))
            resjson = json.loads(response.content)
            if resjson != {"error":"Not found."} and resjson != {'error': 'Not authorized.'}:
                object_list = resjson["rows"]
                for i in object_list:
                    tmp = []
                    for j in i["references"]:
                        tmp.append(j["link_target"])
                    CVE_list.append(tmp)
                for links in CVE_list:
                    cnt = 0
                    for link in links:
                        print(link)
                        try:
                            fp = urlopen(link, timeout=5)
                            mybytes = fp.read()
                            content = mybytes.decode("utf8")
                            fp.close()
                            found = str(content).find(str(version))
                            if found > -1:
                                matched_CVE_list.append(1)
                                cnt += 1
                                break
                        except:
                            continue
                    founded = "Found"
                    if cnt == 0:
                        matched_CVE_list.append(0)
                        founded = "Not Found"
                    print(CVE_list.index(links), object_list[CVE_list.index(links)]["stdcode"][0], founded)
                    print("="*50)
                endtime = datetime.timestamp(datetime.now())
                print("Consumed Time : ", endtime - starttime, " Sec")
            else:
                object_list = []
                matched_CVE_list = []
    return object_list, matched_CVE_list, platform, version

@app.route('/logout')
def logout():
    session.clear()
    oidc.logout()
    return redirect('https://w3.ibm.com')

app.run(host='0.0.0.0',port=8080, debug = True)