import sqlite3
class login:
    def __inti__(self):
        self.log=False
    def signin(self,username,password):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        query="select * from login where username='%s' and password='%s'"
        query=query%(username,password)
        ac=cr.execute(query)
        for a in ac:
            a=list(a)
            self.username=username
            self.password=password
            self.name=a[2]
            self.phone=a[3]
            self.email=a[4]
            self.type=a[5]
        return
    def settings(self,phone,opass,npass):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        ac=cr.execute('select count(*) from login where username=? and phone=? and password=?',(self.username,phone,opass))
        for a in ac:
            su=a
        su = int(su[0])
        if su==1:
            cr.execute('update login set password=? where username=? and phone=?',(npass,self.username,self.phone))
            con.commit()
            return 1
        else:
            return 0
    def feedback(self,description):
        con=sqlite3.connect('sql.db')
        cr=con.cursor()
        cr.execute('insert into issue values(?,?)',(self.username,description))
        con.commit()
        return
        
    def loggedin(self):
        self.log=True
        return
    def loggedout(self):
        self.log=False
