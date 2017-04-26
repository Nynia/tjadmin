# -*-coding=utf-8-*-
from . import main
from app.models import CPUSER,PRODUCTINFO,USER,FOCUSPRODUCT,SPINFO
from flask import render_template

@main.route('/', methods=['GET'])
def root():
    users = USER.query.all()
    spinfos = SPINFO.query.all()
    userlist = []
    for u in users:
        userdict = {}
        userdict['id'] = u.uid
        userdict['name'] = u.username
        userdict['level'] = u.privilege

        namelist = {}
        for item in u.splist.split(','):
            if len(item) < 10:
                spinfo = SPINFO.query.get(item)
                if spinfo:
                    print spinfo
                    namelist[item] = spinfo.spname
            else:
                productinfo = FOCUSPRODUCT.query.get(item)
                if productinfo:
                    namelist[item] = productinfo.servicename
        userdict['namelist'] = namelist
        userlist.append(userdict)

    return render_template('index.html',users=userlist,spinfos = spinfos)

@main.route('/index/<id>', methods=['GET'])
def index(id):
    cpuser = CPUSER.query.get(int(id))
    print cpuser
    return cpuser.cp_name


