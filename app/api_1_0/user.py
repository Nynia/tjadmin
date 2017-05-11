from . import api
from app import db
from flask import jsonify, request
from app.models import USER
import hashlib


@api.route('/user', methods=['POST'])
def update_user():
    username = request.form.get('username')
    password = request.form.get('password')

    level = request.form.get('level')
    splist = request.form.get('splist')
    user = USER.query.filter_by(username=username).first()
    if not user:
        user = USER()

    user.username = username

    print 'passord'
    print user.passwd
    print len(password)
    if len(password) > 0:
        m = hashlib.md5()
        m.update(password)
        user.passwd = m.hexdigest()

    user.privilege = level
    user.splist = splist

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'code': '0',
        'message': 'success',
        'data': user.to_json()
    })

@api.route('/user/<id>', methods=['DELETE'])
def delete_user_by_id(id):
    user = USER.query.get(int(id))
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'code': '0',
            'message': 'success',
            'data': user.to_json()
        })
    else:
        return jsonify({
            'code': '102',
            'message': 'not exist',
            'data': None
        })
