from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Task, Project, db
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get specific task details"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check permissions - user must own the project or be admin
        if not current_user.is_admin() and task.project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assigned_to': task.assigned_to,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'is_overdue': task.is_overdue(),
            'project_id': task.project_id
        }
        
        return jsonify(task_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check permissions
        if not current_user.is_admin() and task.project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            # Mark as completed if status is completed
            if data['status'] == 'completed' and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif data['status'] != 'completed':
                task.completed_at = None
        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')).date()
                except:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            else:
                task.due_date = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'is_overdue': task.is_overdue()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check permissions
        if not current_user.is_admin() and task.project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500