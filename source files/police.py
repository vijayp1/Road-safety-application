import sqlite3
from login import *
class police(login):
    def viewtraffic(self):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        locs=[]
        a=cr.execute('select latitude,longitude from traffic')
        for ac in a:
            ac=list(ac)
            locs.append(ac)
        return(locs)
    def remtraffic(self,pos):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        pos=pos[7:-1].split(',')
        pos[1]=pos[1][6:]
        lat=float(pos[0])
        lon=float(pos[1])
        cr.execute('delete from traffic where latitude=? and longitude=?',(lat,lon))
        con.commit()
        return
