from . import api
from app import db
from flask import jsonify, request
from app.models import BlACKUSER
import datetime

@api.route('/blackuser', methods=['GET'])
def add_new_blackuser():
    username = request.args.get('username')
    password = request.args.get('password')

    blackuser = BlACKUSER.query.filter_by(username=username).first()
    if not blackuser:
        blackuser = BlACKUSER()
        blackuser.username = username
        blackuser.password = password
        blackuser.createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        db.session.add(blackuser)
        db.session.commit()
        return jsonify({
            'code': '0',
            'message': 'success',
            'data': blackuser.to_json()
        })
    else:
        return jsonify({
            'code': '101',
            'message': 'exist',
            'data': None
        })