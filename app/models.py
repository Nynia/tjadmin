from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin

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
    spid = db.Column(db.String(10),primary_key=True)
    spname = db.Column(db.String(255))
    accessno = db.Column(db.String(15))

    def __repr__(self):
        return '<SPINFO %r>' % self.spname

    def to_json(self):
        json_post = {
            'id':self.spid,
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

class BLACKLIST(db.Model):
    __tablename__ = 'black_list'
    id = db.Column(db.String(15),primary_key=True)
    remark = db.Column(db.String(255))
    createtime = db.Column(db.String(14))
    state = db.Column(db.String(1))
    type = db.Column(db.String(1))
    create_mode = db.Column(db.String(1))
    create_person = db.Column(db.String(255))

    def __repr__(self):
        return '<BLACKLIST %r>' % self.id

    def to_json(self):
        json_post = {
            'id':self.id,
            'remark':self.remark,
            'createtime':self.createtime,
            'state':self.state,
            'type':self.type,
            'create_mode':self.create_mode,
            'create_person':self.create_person
        }
        return json_post

class BlACKUSER(UserMixin, db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    createtime = db.Column(db.String(255))

    def __repr__(self):
        return '<USER %s>' % self.username

    def to_json(self):
        json_post = {
            'id': self.id,
            'username':self.username,
            'createtime':self.createtime
        }
        return json_post
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return BlACKUSER.query.get(int(user_id))