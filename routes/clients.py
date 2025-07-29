from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import Client, db
from services.n8n_service import n8n_service

clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

@clients_bp.route('/', methods=['POST'])
@login_required
def create_client():
    """Create a new client (admin only) with N8N integration"""
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
        
        # 🚀 TRIGGER N8N WORKFLOW FOR NEW CLIENT
        client_data = {
            'id': client.id,
            'name': client.name,
            'company': client.company,
            'email': client.email,
            'sector': client.sector
        }
        
        # Trigger N8N workflow asynchronously
        try:
            n8n_service.client_created(client_data)
            print(f"🤖 N8N workflow triggered for new client: {client.name}")
        except Exception as n8n_error:
            print(f"⚠️ N8N trigger failed for client {client.name}: {str(n8n_error)}")
            # Don't fail the client creation if N8N fails
        
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
                'project_count': len(client.projects),
                'created_at': client.created_at.isoformat() if client.created_at else None
            })
        
        return jsonify({
            'clients': clients_data,
            'count': len(clients_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update your routes/clients.py file - specifically the get_client_details function

@clients_bp.route('/<int:client_id>', methods=['GET'])
@login_required
def get_client_details(client_id):
    """Get specific client details with projects"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Get client's projects
        projects_data = []
        for project in client.projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'due_date': project.due_date.isoformat() if project.due_date else None,
                'created_at': project.created_at.isoformat(),
                'owner': project.owner.username,
                'progress': project.get_progress(),
                'task_count': len(project.tasks)
            })
        
        client_data = {
            'id': client.id,
            'name': client.name,
            'company': client.company,
            'email': client.email,
            'sector': client.sector,
            'created_at': client.created_at.isoformat(),
            'projects': projects_data,
            'project_count': len(projects_data)
        }
        
        # 🔧 FIX: Pass the client_data as JSON to the template
        # The template is expecting a client object but we're passing client_data
        return render_template('client/details.html', client=client_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['PUT'])
@login_required
def update_client(client_id):
    """Update client details (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can update clients'}), 403
    
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({'error': 'Client name cannot be empty'}), 400
            client.name = data['name'].strip()
        
        if 'company' in data:
            client.company = data['company'].strip()
        
        if 'email' in data:
            client.email = data['email'].strip()
        
        if 'sector' in data:
            client.sector = data['sector'].strip()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client updated successfully',
            'client': {
                'id': client.id,
                'name': client.name,
                'company': client.company,
                'email': client.email,
                'sector': client.sector,
                'project_count': len(client.projects)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@login_required
def delete_client(client_id):
    """Delete client (admin only) - with safety checks"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can delete clients'}), 403
    
    try:
        client = Client.query.get_or_404(client_id)
        
        # Safety check: Don't delete if client has active projects
        active_projects = [p for p in client.projects if p.status == 'active']
        if active_projects:
            return jsonify({
                'error': f'Cannot delete client with {len(active_projects)} active projects. Please complete or reassign them first.',
                'active_projects': [{'id': p.id, 'name': p.name} for p in active_projects]
            }), 400
        
        # Store client info for response
        client_name = client.name
        client_company = client.company or "No company"
        
        # Delete the client (this will cascade to projects and tasks due to relationships)
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({
            'message': f'Client "{client_name}" ({client_company}) deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>/projects', methods=['GET'])
@login_required
def get_client_projects(client_id):
    """Get all projects for a specific client"""
    try:
        client = Client.query.get_or_404(client_id)
        
        projects_data = []
        for project in client.projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'due_date': project.due_date.isoformat() if project.due_date else None,
                'created_at': project.created_at.isoformat(),
                'owner': project.owner.username,
                'progress': project.get_progress(),
                'task_count': len(project.tasks)
            })
        
        return jsonify({
            'client': {
                'id': client.id,
                'name': client.name,
                'company': client.company
            },
            'projects': projects_data,
            'count': len(projects_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/search', methods=['GET'])
@login_required  
def search_clients():
    """Search clients by name, company, or sector"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'clients': [], 'count': 0}), 200
        
        # Search in name, company, and sector fields
        clients = Client.query.filter(
            db.or_(
                Client.name.ilike(f'%{query}%'),
                Client.company.ilike(f'%{query}%'),
                Client.sector.ilike(f'%{query}%')
            )
        ).all()
        
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
            'count': len(clients_data),
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500