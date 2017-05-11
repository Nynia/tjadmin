from . import api
from flask import jsonify, request
from app.models import BLACKLIST

@api.route('/blacklist/<id>', methods=['GET'])
def get_by_num(id):
    blackitem = BLACKLIST.query.get(id)
    if blackitem:
        return jsonify({
            'code': '0',
            'message': 'success',
            'data': blackitem.to_json()
        })
    else:
        return jsonify({
            'code': '102',
            'message': 'not exist',
            'data': None
        })
