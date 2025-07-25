# Create this file as routes/users.py

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import User

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/', methods=['GET'])
@login_required
def get_users():
    """Get all users for project assignment"""
    try:
        # Only admins can see all users, employees see only themselves
        if current_user.is_admin():
            users = User.query.all()
        else:
            users = [current_user]
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'users': users_data,
            'count': len(users_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get specific user details"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Only admins can see other users, employees can only see themselves
        if not current_user.is_admin() and user.id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500