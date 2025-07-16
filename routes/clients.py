from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Client, db

clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

@clients_bp.route('/', methods=['POST'])
@login_required
def create_client():
    """Create a new client (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can create clients'}), 403
    
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Client name is required'}), 400
        
        client = Client(
            name=data['name'],
            company=data.get('company', ''),
            email=data.get('email', ''),
            sector=data.get('sector', '')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'message': 'Client created successfully',
            'client': {
                'id': client.id,
                'name': client.name,
                'company': client.company,
                'email': client.email,
                'sector': client.sector
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/', methods=['GET'])
@login_required
def get_clients():
    """Get all clients"""
    try:
        clients = Client.query.all()
        
        clients_data = []
        for client in clients:
            clients_data.append({
                'id': client.id,
                'name': client.name,
                'company': client.company,
                'email': client.email,
                'sector': client.sector,
                'project_count': len(client.projects)
            })
        
        return jsonify({
            'clients': clients_data,
            'count': len(clients_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500