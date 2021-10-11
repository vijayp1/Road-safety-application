import sqlite3
from login import *
class doctor(login):
    def getaccidentlocations(self):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        a=cr.execute("select latitude,longitude from accident where status='nill'")
        accidents=[]
        for s in a:
            s=list(s)
            accidents.append(s)
        try:
            b=cr.execute("select latitude,longitude from assign where assigneduser=?",(self.username))
            for s in b:
                s=list(s)
                accidents.append(s)
        except Exception as e:
            accidents=accidents
        return(accidents)
    def accept(self,acc):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        acc=acc[7:-1].split(',')
        acc[1]=acc[1][6:]
        lat=float(acc[0])
        lon=float(acc[1])
        cr.execute('update accident set status="accept" where latitude=? and longitude=?',(lat,lon))
        con.commit()
        cr.execute('insert into assign values(?,?,?)',(lat,lon,self.username))
        con.commit()
        return
    def reached(self,acc,hos):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        acc=acc[7:-1].split(',')
        acc[1]=acc[1][6:]
        alat=float(acc[0])
        alon=float(acc[1])
        hos=hos[7:-1].split(',')
        hos[1]=hos[1][6:]
        hlat=float(hos[0])
        hlon=float(hos[1])
        url="https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=driving"
        apos=str(alat)+','+str(alon)
        hpos=str(hlat)+','+str(hlon)
        url=url%(apos,hpos)
        
        cr.execute('update accident set status="reached" where latitude=? and longitude=?',(alat,alon))
        con.commit()
        return(url)
    def complete(self,acc):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        acc=acc[7:-1].split(',')
        acc[1]=acc[1][6:]
        lat=float(acc[0])
        lon=float(acc[1])
        cr.execute('delete from accident where latitude=? and longitude=?',(lat,lon))
        cr.execute('delete from assign where latitude=? and longitude=?',(lat,lon))
        con.commit()
        return
