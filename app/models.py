from app import db

class CPUSER(db.Model):
    __tablename__ = 'cp_user'
    __bind_key__ = 'jstelecom'

    cp_id = db.Column(db.Integer,primary_key=True)
    cp_name = db.Column(db.String(32))
    cp_access_num = db.Column(db.String(50))
    cp_company_name = db.Column(db.String(100))
    cp_company_addr = db.Column(db.String(150))
    cp_status_update_url = db.Column(db.String(150))
    createtime = db.Column(db.DateTime)
    verify_status = db.Column(db.Integer)
    sp_id = db.Column(db.String(10))


    def __repr__(self):
        return '<CPUSER %r>' % self.cp_name

class PRODUCTINFO(db.Model):
    __tablename__ = 'product_info'
    __bind_key__ = 'jstelecom'

    product_id = db.Column(db.Integer, primary_key=True)
    cp_id = db.Column(db.Integer)
    ismp_product_id = db.Column(db.String(30))
    ismp_business_id = db.Column(db.String(30))
    access_num = db.Column(db.String(10))
    product_name = db.Column(db.String(32))
    order_string = db.Column(db.String(32))
    td_orderstring = db.Column(db.String(32))
    orderstring_type = db.Column(db.Integer)
    price = db.Column(db.Integer)
    verify_status = db.Column(db.Integer)
    createtime = db.Column(db.DateTime)

    def __repr__(self):
        return '<PRODUCTINFO %r>' % self.product_id

class USER(db.Model):
    __tablename__ = 'user'
    __bind_key__ = 'ora11g'
    uid = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    passwd = db.Column(db.String(50))
    privilege = db.Column(db.String(1))
    splist = db.Column(db.String(500))

    def __repr__(self):
        return '<USER %r>' % self.username

    def to_json(self):
        json_post = {
            'uid': self.uid,
            'username':self.username,
            'privilege':self.privilege,
            'splist':self.splist
        }
        return json_post

class SPINFO(db.Model):
    __tablename__ = 'focused_sp_info'
    __bind_key__ = 'ora11g'
    id = db.Column(db.Integer,primary_key=True)
    spname = db.Column(db.String(255))
    accessno = db.Column(db.String(15))

    def __repr__(self):
        return '<SPINFO %r>' % self.spname

    def to_json(self):
        json_post = {
            'id':self.id,
            'spname':self.spname,
            'accessno':self.accessno
        }
        return json_post

class FOCUSPRODUCT(db.Model):
    __tablename__ = 'focused_product_info'
    __bind_key__ = 'ora11g'
    serviceid = db.Column(db.String(30),primary_key=True)
    servicename = db.Column(db.String(100))
    spid = db.Column(db.String(10))
    orderflag = db.Column(db.String(1))

    def __repr__(self):
        return '<FOCUSPRODUCT %r>' % self.servicename