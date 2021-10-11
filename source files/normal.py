import sqlite3
from login import *
class normal(login):
    def reporttraffic(self,pos):
        pos=pos[1:-1].split(',')
        lat=float(pos[0])
        lon=float(pos[1][1:])
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        cr.execute('insert into traffic values(?,?,?)',(self.username,lat,lon))
        con.commit()
        return
    def reportaccident(self,pos):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        pos=pos[1:-1].split(',')
        pos[1]=pos[1][1:]
        lat=float(pos[0])
        lon=float(pos[1])
        cr.execute('insert into accident values(?,?,?,?)',(self.username,lat,lon,"nill"))
        con.commit()
        url="https://www.google.com/maps/search/?api=1&query="
        pos=str(lat)+','+str(lon)
        url=url+pos
        
        return(url)
    def viewaccident(self):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        locs=[]
        a=cr.execute('select latitude,longitude from accident')
        for ac in a:
            ac=list(ac)
            locs.append(ac)
        return(locs)
    def viewtraffic(self):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        locs=[]
        a=cr.execute('select latitude,longitude from traffic')
        for ac in a:
            ac=list(ac)
            locs.append(ac)
        return(locs)
