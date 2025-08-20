# src/routes/user.py

from flask import Blueprint, jsonify
# Importe 'db' do diretório pai (src).
from .. import db
# Importe os modelos necessários do diretório 'models'.
from ..models.user import User

# Crie o Blueprint.
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
