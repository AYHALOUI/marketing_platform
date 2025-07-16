from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Project, Task, db
from datetime import datetime

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/', methods=['GET'])
@login_required
def get_projects():
    """Get all projects for current user or all projects for admin"""
    try:
        if current_user.is_admin():
            # Admin can see all projects
            projects = Project.query.all()
        else:
            # Employee can only see their own projects
            projects = Project.query.filter_by(user_id=current_user.id).all()
        
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'due_date': project.due_date.isoformat() if project.due_date else None,
                'created_at': project.created_at.isoformat(),
                'owner': project.owner.username,
                'owner_id': project.user_id,
                'progress': project.get_progress(),
                'task_count': len(project.tasks)
            })
        
        return jsonify({
            'projects': projects_data,
            'count': len(projects_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """Get specific project details"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Check permissions
        if not current_user.is_admin() and project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get project tasks
        tasks_data = []
        for task in project.tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat(),
                'is_overdue': task.is_overdue()
            })
        
        project_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'status': project.status,
            'due_date': project.due_date.isoformat() if project.due_date else None,
            'created_at': project.created_at.isoformat(),
            'owner': project.owner.username,
            'owner_id': project.user_id,
            'progress': project.get_progress(),
            'tasks': tasks_data,
            'task_count': len(tasks_data)
        }
        
        return jsonify(project_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/', methods=['POST'])
@login_required
def create_project():
    """Create a new project (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can create projects'}), 403
    
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        # Check if assigned_to user exists
        assigned_user_id = data.get('assigned_to')
        if assigned_user_id:
            from models import User
            assigned_user = User.query.get(assigned_user_id)
            if not assigned_user:
                return jsonify({'error': 'Assigned user not found'}), 400
        else:
            return jsonify({'error': 'Please assign the project to a user'}), 400
        
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')).date()
            except:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'active'),
            due_date=due_date,
            user_id=assigned_user_id,
            client_id=data.get('client_id')  # ADD THIS LINE
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'due_date': project.due_date.isoformat() if project.due_date else None,
                'created_at': project.created_at.isoformat(),
                'owner': project.owner.username,
                'assigned_to': assigned_user.username
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """Update project (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can update projects'}), 403
    
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    project.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')).date()
                except:
                    project.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            else:
                project.due_date = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'due_date': project.due_date.isoformat() if project.due_date else None,
                'progress': project.get_progress()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete project (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can delete projects'}), 403
    
    try:
        project = Project.query.get_or_404(project_id)
        
        # Delete project (cascades to tasks due to relationship setup)
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:project_id>/tasks', methods=['POST'])
@login_required
def add_task_to_project(project_id):
    """Add a task to a project"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Check permissions
        if not current_user.is_admin() and project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Task title is required'}), 400
        
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')).date()
            except:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'todo'),
            assigned_to=data.get('assigned_to', ''),
            due_date=due_date,
            project_id=project_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task added successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500