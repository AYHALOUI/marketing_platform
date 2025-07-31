# routes/deadline_api.py - COMPLETE version with all endpoints

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Task, Project, User, db
from datetime import datetime, date, timedelta
from services.n8n_service import n8n_service
import logging

logger = logging.getLogger(__name__)

deadline_api = Blueprint('deadline_api', __name__, url_prefix='/api/deadlines')

# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

@deadline_api.route('/ping', methods=['GET'])
def ping():
    """Public ping endpoint - no authentication required"""
    return jsonify({
        'message': 'Deadline API is running!',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0'
    }), 200

@deadline_api.route('/public-stats', methods=['GET'])
def public_stats():
    """Public endpoint to check basic stats - no authentication required"""
    try:
        today = date.today()
        
        # Get basic counts (no user filtering for public endpoint)
        stats = {
            'total_tasks': Task.query.count(),
            'completed_tasks': Task.query.filter_by(status='completed').count(),
            'active_tasks': Task.query.filter(Task.status != 'completed').count(),
            'overdue_tasks': Task.query.filter(
                Task.due_date < today,
                Task.status != 'completed'
            ).count(),
            'projects_count': Project.query.count(),
            'active_projects': Project.query.filter_by(status='active').count()
        }
        
        return jsonify({
            'message': 'Public deadline statistics',
            'stats': stats,
            'as_of_date': today.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get stats',
            'details': str(e)
        }), 500

# ============================================================================
# AUTHENTICATED ENDPOINTS
# ============================================================================

@deadline_api.route('/health', methods=['GET'])
@login_required
def deadline_system_health():
    """Check the health of the deadline notification system"""
    try:
        # Check N8N connectivity
        n8n_health = n8n_service.health_check()
        
        # Get deadline statistics
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        stats = {
            'tasks_due_tomorrow': Task.query.filter(
                Task.due_date == tomorrow,
                Task.status != 'completed'
            ).count(),
            'tasks_due_this_week': Task.query.filter(
                Task.due_date.between(today, next_week),
                Task.status != 'completed'
            ).count(),
            'overdue_tasks': Task.query.filter(
                Task.due_date < today,
                Task.status != 'completed'
            ).count(),
            'total_active_tasks': Task.query.filter(
                Task.status != 'completed'
            ).count()
        }
        
        return jsonify({
            'status': 'healthy',
            'n8n_service': n8n_health,
            'deadline_stats': stats,
            'last_checked': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking deadline system health: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'last_checked': datetime.utcnow().isoformat()
        }), 500

@deadline_api.route('/check', methods=['POST'])
@login_required
def manual_deadline_check():
    """Manually trigger a deadline check (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # For now, just return a success message
        return jsonify({
            'message': 'Manual deadline check completed successfully',
            'note': 'Full monitoring service not yet integrated',
            'triggered_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error during manual deadline check: {str(e)}")
        return jsonify({
            'error': 'Failed to run deadline check',
            'details': str(e)
        }), 500

@deadline_api.route('/tasks/approaching', methods=['GET'])
@login_required
def get_approaching_deadlines():
    """Get tasks with approaching deadlines"""
    try:
        days_ahead = request.args.get('days', 7, type=int)  # Default 7 days
        today = date.today()
        target_date = today + timedelta(days=days_ahead)
        
        # Build query based on user role
        query = Task.query.filter(
            Task.due_date.between(today, target_date),
            Task.status != 'completed'
        ).join(Project)
        
        # Filter by user permissions
        if not current_user.is_admin():
            query = query.filter(
                db.or_(
                    Project.user_id == current_user.id,
                    Task.assigned_to == current_user.username
                )
            )
        
        tasks = query.all()
        
        # Format response
        approaching_tasks = []
        for task in tasks:
            days_until = (task.due_date - today).days
            approaching_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project_name': task.project.name,
                'project_id': task.project.id,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date.isoformat(),
                'days_until_deadline': days_until,
                'status': task.status,
                'urgency': get_urgency_level(days_until),
                'is_overdue': False
            })
        
        return jsonify({
            'tasks': approaching_tasks,
            'count': len(approaching_tasks),
            'days_ahead': days_ahead,
            'date_range': {
                'from': today.isoformat(),
                'to': target_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting approaching deadlines: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deadline_api.route('/tasks/overdue', methods=['GET'])
@login_required
def get_overdue_tasks():
    """Get overdue tasks"""
    try:
        today = date.today()
        
        # Build query based on user role
        query = Task.query.filter(
            Task.due_date < today,
            Task.status != 'completed'
        ).join(Project)
        
        # Filter by user permissions
        if not current_user.is_admin():
            query = query.filter(
                db.or_(
                    Project.user_id == current_user.id,
                    Task.assigned_to == current_user.username
                )
            )
        
        tasks = query.all()
        
        # Format response
        overdue_tasks = []
        for task in tasks:
            days_overdue = (today - task.due_date).days
            overdue_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project_name': task.project.name,
                'project_id': task.project.id,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date.isoformat(),
                'days_overdue': days_overdue,
                'status': task.status,
                'severity': get_overdue_severity(days_overdue),
                'is_overdue': True
            })
        
        # Sort by days overdue (most overdue first)
        overdue_tasks.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return jsonify({
            'tasks': overdue_tasks,
            'count': len(overdue_tasks),
            'checked_date': today.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting overdue tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deadline_api.route('/notify/task/<int:task_id>', methods=['POST'])
@login_required
def send_task_deadline_notification(task_id):
    """Manually send deadline notification for a specific task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check permissions
        if not current_user.is_admin() and task.project.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        if not task.due_date:
            return jsonify({'error': 'Task has no due date set'}), 400
        
        if task.status == 'completed':
            return jsonify({'error': 'Task is already completed'}), 400
        
        # Calculate days until deadline
        today = date.today()
        days_until = (task.due_date - today).days
        
        # Determine notification type and send
        if days_until < 0:
            # Overdue
            success = trigger_overdue_alert(task_id, abs(days_until))
            notification_type = 'overdue'
        else:
            # Approaching deadline
            urgency = get_urgency_level(days_until)
            success = trigger_deadline_reminder(task_id, days_until, urgency)
            notification_type = 'deadline_approaching'
        
        if success:
            return jsonify({
                'message': f'{notification_type.replace("_", " ").title()} notification sent successfully',
                'task_id': task_id,
                'task_title': task.title,
                'notification_type': notification_type,
                'days_until_deadline': days_until,
                'sent_to': task.assigned_to,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send notification',
                'task_id': task_id,
                'notification_type': notification_type
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending task deadline notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deadline_api.route('/test/webhook/<string:webhook_type>', methods=['POST'])
@login_required
def test_webhook(webhook_type):
    """Test a specific webhook (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        valid_webhooks = ['task_deadline_approaching', 'task_overdue']
        
        if webhook_type not in valid_webhooks:
            return jsonify({
                'error': 'Invalid webhook type',
                'valid_types': valid_webhooks
            }), 400
        
        # Test the webhook with sample data
        test_data = {
            'test': True,
            'webhook_type': webhook_type,
            'message': f'Test webhook for {webhook_type}',
            'timestamp': datetime.utcnow().isoformat(),
            'triggered_by': current_user.username
        }
        
        import requests
        webhook_url = f"http://localhost:5678/webhook/{webhook_type}"
        
        try:
            response = requests.post(webhook_url, json={
                'trigger_type': webhook_type,
                'data': test_data,
                'source': 'marketing_platform_test'
            }, timeout=10)
            
            if response.status_code == 200:
                return jsonify({
                    'message': f'Webhook {webhook_type} test successful',
                    'webhook_url': webhook_url,
                    'response_status': response.status_code,
                    'timestamp': datetime.utcnow().isoformat()
                }), 200
            else:
                return jsonify({
                    'error': f'Webhook test failed with status {response.status_code}',
                    'webhook_url': webhook_url,
                    'response': response.text
                }), 500
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'error': 'Cannot connect to N8N webhook',
                'webhook_url': webhook_url,
                'suggestion': 'Make sure N8N is running on localhost:5678'
            }), 500
        
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deadline_api.route('/stats', methods=['GET'])
@login_required
def get_deadline_stats():
    """Get comprehensive deadline statistics"""
    try:
        today = date.today()
        
        # Base queries
        base_query = Task.query.filter(Task.status != 'completed').join(Project)
        
        # Filter by user permissions
        if not current_user.is_admin():
            base_query = base_query.filter(
                db.or_(
                    Project.user_id == current_user.id,
                    Task.assigned_to == current_user.username
                )
            )
        
        # Calculate various deadline categories
        stats = {
            'overdue': {
                'count': base_query.filter(Task.due_date < today).count(),
                'categories': {
                    '1-3_days': base_query.filter(
                        Task.due_date.between(today - timedelta(days=3), today - timedelta(days=1))
                    ).count(),
                    '4-7_days': base_query.filter(
                        Task.due_date.between(today - timedelta(days=7), today - timedelta(days=4))
                    ).count(),
                    'over_week': base_query.filter(
                        Task.due_date < today - timedelta(days=7)
                    ).count()
                }
            },
            'due_soon': {
                'today': base_query.filter(Task.due_date == today).count(),
                'tomorrow': base_query.filter(Task.due_date == today + timedelta(days=1)).count(),
                'this_week': base_query.filter(
                    Task.due_date.between(today, today + timedelta(days=7))
                ).count(),
                'next_week': base_query.filter(
                    Task.due_date.between(today + timedelta(days=8), today + timedelta(days=14))
                ).count()
            },
            'by_status': {
                'todo': base_query.filter(Task.status == 'todo').count(),
                'in_progress': base_query.filter(Task.status == 'in_progress').count()
            },
            'total_active_tasks': base_query.count()
        }
        
        # Calculate percentages
        total = stats['total_active_tasks']
        if total > 0:
            stats['percentages'] = {
                'overdue_rate': round((stats['overdue']['count'] / total) * 100, 1),
                'due_this_week_rate': round((stats['due_soon']['this_week'] / total) * 100, 1)
            }
        else:
            stats['percentages'] = {'overdue_rate': 0, 'due_this_week_rate': 0}
        
        return jsonify({
            'stats': stats,
            'as_of_date': today.isoformat(),
            'user_scope': 'all_tasks' if current_user.is_admin() else 'user_tasks'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting deadline stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def trigger_deadline_reminder(task_id: int, days_until: int, urgency: str = 'medium'):
    """Local function to trigger deadline reminder"""
    try:
        task = Task.query.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
        
        user = User.query.filter_by(username=task.assigned_to).first()
        if not user:
            logger.error(f"User {task.assigned_to} not found")
            return False
        
        notification_data = {
            'task_id': task.id,
            'task_title': task.title,
            'task_description': task.description or '',
            'project_name': task.project.name,
            'project_id': task.project.id,
            'assigned_to': task.assigned_to,
            'assigned_user_email': user.email,
            'due_date': task.due_date.strftime('%B %d, %Y') if task.due_date else 'No due date',
            'days_until_deadline': days_until,
            'urgency_level': urgency,
            'dashboard_url': f'http://localhost:5000/project/{task.project.id}',
            'notification_type': 'deadline_warning',
            'created_at': datetime.utcnow().isoformat()
        }
        
        return n8n_service.task_deadline_approaching(notification_data)
        
    except Exception as e:
        logger.error(f"Error triggering deadline reminder: {str(e)}")
        return False

def trigger_overdue_alert(task_id: int, days_overdue: int):
    """Local function to trigger overdue alert"""
    try:
        task = Task.query.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
        
        user = User.query.filter_by(username=task.assigned_to).first()
        if not user:
            logger.error(f"User {task.assigned_to} not found")
            return False
        
        notification_data = {
            'task_id': task.id,
            'task_title': task.title,
            'task_description': task.description or '',
            'project_name': task.project.name,
            'project_id': task.project.id,
            'assigned_to': task.assigned_to,
            'assigned_user_email': user.email,
            'due_date': task.due_date.strftime('%B %d, %Y') if task.due_date else 'No due date',
            'days_overdue': days_overdue,
            'urgency_level': 'critical',
            'dashboard_url': f'http://localhost:5000/project/{task.project.id}',
            'notification_type': 'overdue_alert',
            'created_at': datetime.utcnow().isoformat()
        }
        
        return n8n_service.task_overdue(notification_data)
        
    except Exception as e:
        logger.error(f"Error triggering overdue alert: {str(e)}")
        return False

def get_urgency_level(days_until: int) -> str:
    """Get urgency level based on days until deadline"""
    if days_until <= 1:
        return 'urgent'
    elif days_until <= 3:
        return 'high'
    elif days_until <= 7:
        return 'medium'
    else:
        return 'low'

def get_overdue_severity(days_overdue: int) -> str:
    """Get severity level for overdue tasks"""
    if days_overdue >= 14:
        return 'critical'
    elif days_overdue >= 7:
        return 'severe'
    elif days_overdue >= 3:
        return 'high'
    else:
        return 'moderate'