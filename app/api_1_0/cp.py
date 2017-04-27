from . import api
from app import db
from flask import jsonify,request
from app.models import CPUSER

@api.route('/sp', methods=['POST'])
def add_new_cp():
    pass

