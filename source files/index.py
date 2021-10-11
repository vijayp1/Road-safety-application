import sqlite3
import smtplib,ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request,redirect,url_for
from geopy.geocoders import Nominatim
import requests
from bs4 import BeautifulSoup
from normal import *
from police import *
from doctor import *



con=sqlite3.connect('sql.db')
cr=con.cursor()
email = 'rsawebapp@gmail.com'
password = 'Qwerty@0022'
server = smtplib.SMTP(host='smtp.gmail.com',port=587)
server.starttls()
server.login(email, password)

app = Flask(__name__)

def send_email(send_to_email,subject,url):
    global server
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(url, 'plain'))
    server.send_message(msg)
    del msg

def location():
    url="https://www.google.com/search?q=my+location"
    r=requests.get(url)
    s=BeautifulSoup(r.content,"html.parser")
    l=s.find("span",id="xxxXMc").string
    address=l
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(address)
    return(location.latitude, location.longitude)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/signup/')
def signup():
    return render_template('signup.html')
@app.route('/register',methods=["POST"])
def register():
    con=sqlite3.connect('sql.db')
    cr=con.cursor()
    user=request.form['usrid']
    name=request.form['name']
    pas=request.form['pass']
    ph=request.form['phno']
    ema=request.form['email']
    typ=request.form['typeu']
    if user=="" or name=="" or pas=="" or ph=="" or ema=="" or typ=="":
        msg='incomplete'
        return render_template('signup.html',msg=msg)
    if ema[-10:]!="@gmail.com":
        msg='emailformat'
        return render_template('signup.html',msg=msg)
    if len(ph)!=10:
        msg='phoneformat'
        return render_template('signup.html',msg=msg)
    query="select count(*) from login where username='%s' or email='%s' or phone='%s'"
    query=query%(user,ema,ph)
    ac=cr.execute(query)
    su=0
    for a in ac:
        su=a
    su=int(su[0])
    if su==1:
        msg='exist'
        return render_template('signup.html',msg=msg)
    query="insert into login values('%s','%s','%s','%s','%s','%s')"
    query=query%(user,pas,name,ph,ema,typ)
    cr.execute(query)
    con.commit()
    msg="created"
    return render_template('index.html',msg=msg)

@app.route('/forgotpass/')
def forgotpass():
    return render_template('forgotpass.html')

@app.route('/checkpass',methods=["POST"])
def checkpass():
    con=sqlite3.connect('sql.db')
    cr=con.cursor()
    user=request.form['fusr']
    phn=request.form['fphno']
    pas=request.form['fpass']
    if user=="" or phn=="" or pas=="":
        msg="incomplete"
        return render_template('forgotpass.html',msg=msg)
    a=0
    query="select count(*) from login where username='%s' and phone='%s'"
    query=query%(user,phn)
    a=cr.execute(query)
    for i in a:
        su=i[0]
    if su==1:
        query="update login set password='%s' where username='%s' and phone='%s'"
        query=query%(pas,user,phn)
        cr.execute(query)
        con.commit()
        msg="changed"
        return render_template('index.html',msg=msg)
    else:
        msg="incorrect"
        return render_template('forgotpass.html',msg=msg)

@app.route('/log',methods=["POST","GET"])
def log():
    global obj,lati,longi
    con=sqlite3.connect('sql.db')
    cr=con.cursor()
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if username=="" or password=="":
            msg='incomplete'
            return render_template('index.html',msg=msg)
        ac=cr.execute('SELECT count(*) FROM login WHERE username = ? AND password = ?', (username, password ))
        for a in ac:
            su=a
        su=int(su[0])
        if su==1:
            query="select type from login where username = '%s'"
            query=query%(username)
            ac=cr.execute(query)
            for a in ac:
                logtype=a
            logtype=list(logtype)[0]
            if logtype=='normal':
                obj = normal()
                obj.signin(username,password)
                obj.loggedin()
            if logtype=='police':
                obj=police()
                obj.signin(username,password)
                obj.loggedin()
            if logtype=='doctor':
                obj=doctor()
                obj.signin(username,password)
                obj.loggedin()
            msg="in"
            try:
                lati,longi = location()
            except Exception as e:
                lati='16.761139082237044'
                longi='81.83448893398199'
                msg="cantidentify"
            return render_template('home.html', msg = msg,logtype=obj.type)
        else:
            msg = 'incorrect'
            return render_template('index.html', msg = msg)

@app.route('/feedback',methods=["POST"])
def feedback():
    global obj
    if obj.log==True:
        desc=request.form['desc']
        if desc=="":
            msg="incomplete"
            return render_template('home.html',msg=msg,logtype=obj.type)
        obj.feedback(desc)
        send_email('vijayreddy0022@gmail.com',"issue reported",desc)
        msg="submitted"
        return render_template('home.html',msg=msg,logtype=obj.type)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/home/')
def home():
    global obj
    if obj.log==True:
        return render_template('home.html',logtype=obj.type)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/settings/')
def settings():
    global obj
    if obj.log==True:
        return render_template('settings.html',logtype=obj.type)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/changepass',methods=["POST"])
def changepass():
    global obj
    if obj.log==True:
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        phn=request.form['fphno']
        opas=request.form['opass']
        npas=request.form['fpass']
        if phn=="" or opas=="" or npas=="":
            msg="incomplete"
            return render_template('settings.html',msg=msg,logtype=obj.type)
        query="select count(*) from login where username='%s' and phone='%s' and password='%s'"
        query=query%(obj.username,phn,opas)
        a=cr.execute(query)
        for i in a:
            su=i[0]
        if su==1:
            query="update login set password='%s' where username='%s' and phone='%s'"
            query=query%(npas,obj.username,phn)
            cr.execute(query)
            con.commit()
            msg="changed"
            return render_template('home.html',msg=msg,logtype=obj.type)
        else:
            msg="incorect"
            return render_template('settings.html',msg=msg,logtype=obj.type)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/signout/')
def signout():
    global obj
    obj.loggedout()
    return redirect(url_for('index'))

@app.route('/reporttr/')
def reporttr():
    global obj
    
    if obj.log==True:
        return render_template('reporttr.html',logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/reporttraffic',methods=["POST"])
def reporttraffic():
    global obj
    if obj.log==True:
        pos=request.form['latlng']
        if pos=="":
            msg="nolocation"
            return render_template('reporttr.html',msg=msg,lati=lati,longi=longi)
        obj.reporttraffic(pos)
        msg="reported"
        return render_template('reporttr.html',msg=msg,logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/accview/')
def accview():
    global obj
    if obj.log==True:
        locs=obj.viewaccident()
        return render_template('accview.html',locs=locs,logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/viewtr/')
def viewtr():
    global obj
    if obj.log==True:
        locs=obj.viewtraffic()
        return render_template('viewtr.html',locs=locs,logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/reportac/')
def reportac():
    global obj
    if obj.log==True:
        return render_template('reportacc.html',logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/reportaccident',methods=["POST"])
def reportaccident():
    global obj
    if obj.log==True:
        pos=request.form['latlng']
        if pos=="":
            msg="nolocation"
            return render_template('reportacc.html',msg=msg,logtype=obj.type,lati=lati,longi=longi)
        url=obj.reportaccident(pos)
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        q=cr.execute("select email from login where type='doctor'")
        for i in q:
            send_email(i[0],"accident",url)
        msg="reported"
        return render_template('reportacc.html',msg=url,logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/edittr/')
def edittr():
    global obj
    if obj.log==True:
        locs=obj.viewtraffic()
        return render_template('edittr.html',locs=locs,logtype=obj.type,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/remtr',methods=["POST"])
def remtr():
    global obj
    if obj.log==True:
        pos=request.form['pos']
        if pos=="":
            msg="nolocation"
            locs=obj.viewtraffic()
            return render_template('edittr.html',locs=locs,logtype=obj.type,lati=lati,longi=longi)
        obj.remtraffic(pos)
        locs=obj.viewtraffic()
        msg="removed"
        return render_template('edittr.html',msg=msg,logtype=obj.type,locs=locs,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg,logtype=obj.type)

@app.route('/viewac/')
def viewac():
    global obj
    if obj.log==True:
        alocs=obj.getaccidentlocations()
        f=open('hospitals.json')
        data=json.loads(f.read())
        hlocs=[]
        for i in data['hospitals']:
            a=i['location']
            a=a.split(',')
            a[0]=float(a[0])
            a[1]=float(a[1][1:])
            hlocs.append(a)
        f.close()
        return render_template('viewac.html',alocs=alocs,logtype=obj.type,hlocs=hlocs,lati=lati,longi=longi)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

@app.route('/modifyac',methods=["POST"])
def modifyac():
    global obj
    if obj.log==True:
        acc=request.form['alatlng']
        hos=request.form['hlatlng']
        stat=request.form['status']
        if acc=="":
            msg="nolocation"
            return render_template('error.html',msg=msg,logtype=obj.type)
        if stat=='accept':
            obj.accept(acc)
            msg="assigned"
            return render_template('home.html',msg=msg,logtype=obj.type)
        if stat=='reached':
            if hos=="":
                msg="nolocation"
                return render_template('error.html',msg=msg,logtype=obj.type)
            url=obj.reached(acc,hos)
            con=sqlite3.connect('sql.db')
            cr=con.cursor()
            q=cr.execute("select email from login where type='police'")
            for i in q:
                send_email(i[0],'ambulance waypoint',url)
            send_email(obj.email,'ambulance waypoint',url)
            msg="waypoint"
            return render_template('home.html',msg=msg,logtype=obj.type)
        if stat=='complete':
            obj.complete(acc)
            msg="closed"
            return render_template('success.html',msg=msg,logtype=obj.type)
    else:
        msg="out"
        return render_template('index.html',msg=msg)

global obj
global lati
global longi
app.debug=True
app.run()
