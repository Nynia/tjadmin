from . import api
from app import db
from flask import jsonify,request
from app.models import SPINFO

@api.route('/sp/<id>', methods=['DELETE'])
def delete_sp_by_id(id):
    sp = SPINFO.query.get(int(id))
    if sp:
        db.session.delete(sp)
        db.session.commit()
        return jsonify({
            'code': '0',
            'message': 'success',
            'data': sp.to_json()
        })
    else:
        return jsonify({
            'code': '102',
            'message': 'not exist',
            'data': None
        })
@api.route('/sp', methods=['POST'])
def add_new_sp():
    id = request.form.get('id')
    name = request.form.get('spname')
    accessno = request.form.get('accessno')

    if not SPINFO.query.get(int(id)):
        spinfo = SPINFO()
        spinfo.id = id
        spinfo.spname = name
        spinfo.accessno = accessno

        db.session.add(spinfo)
        db.session.commit()
        return jsonify({
            'code': '0',
            'message': 'success',
            'data': spinfo.to_json()
        })
    else:
        return jsonify({
            'code': '101',
            'message': 'exist',
            'data': None
        })