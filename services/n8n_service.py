# Updated services/n8n_service.py - Add these methods

import requests
import json
import os
from datetime import datetime
from models import AutomationTrigger, db

class N8NService:
    def __init__(self):
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook-test')
    
    def trigger_workflow(self, trigger_type, data, project_id=None):
        try:
            # Prepare payload for N8N
            payload = {
                'trigger_type': trigger_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data,
                'source': 'marketing_platform'
            }
            
            # Send to N8N webhook
            webhook_endpoint = f"{self.webhook_url}/{trigger_type}"
            
            response = requests.post(
                webhook_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:                
                self._log_automation_trigger(trigger_type, payload, project_id, 'success')
                return True
            else:
                self._log_automation_trigger(trigger_type, payload, project_id, 'failed')
                return False
                
        except requests.exceptions.RequestException as e:
            self._log_automation_trigger(trigger_type, data, project_id, 'connection_failed')
            return False
        except Exception as e:
            return False
    
    def _log_automation_trigger(self, trigger_type, data, project_id, status):
        """Log automation trigger in database"""
        try:
            trigger = AutomationTrigger(
                trigger_name=f"Auto: {trigger_type}",
                trigger_type=trigger_type,
                n8n_webhook_url=f"{self.webhook_url}/{trigger_type}",
                trigger_data=json.dumps(data),
                is_active=True,
                project_id=project_id
            )
            db.session.add(trigger)
            db.session.commit()
            
        except Exception as e:
            print(f"📝 Failed to log automation trigger: {str(e)}")
    
    # Existing methods...
    def user_registered(self, user_data):
        """Trigger when a new user registers - Send welcome email"""
        return self.trigger_workflow('user_registered', {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'role': user_data.get('role'),
            'registration_date': user_data.get('registration_date'),
            'platform_url': 'http://localhost:5000',
            'support_email': 'support@tm-holding.ma'
        })
    
    def client_created(self, client_data):
        """Trigger when a new client is created"""
        return self.trigger_workflow('client_created', {
            'client_id': client_data.get('id'),
            'client_name': client_data.get('name'),
            'company': client_data.get('company'),
            'email': client_data.get('email'),
            'sector': client_data.get('sector')
        })
        
    def project_created(self, project_data):
        """Trigger when a new project is created"""
        return self.trigger_workflow('project_created', {
            'project_id': project_data.get('id'),
            'project_name': project_data.get('name'),
            'client_name': project_data.get('client_name'),
            'owner': project_data.get('owner'),
            'due_date': project_data.get('due_date'),
            'status': project_data.get('status')
        }, project_id=project_data.get('id'))
    
    def task_created(self, task_data):
        """Trigger when a new task is created - Send notification to assigned user"""
        return self.trigger_workflow('task_created', {
            'task_id': task_data.get('id'),
            'task_title': task_data.get('title'),
            'task_description': task_data.get('description'),
            'project_name': task_data.get('project_name'),
            'project_id': task_data.get('project_id'),
            'assigned_to': task_data.get('assigned_to'),
            'assigned_user_email': task_data.get('assigned_user_email'),
            'due_date': task_data.get('due_date'),
            'status': task_data.get('status'),
            'created_by': task_data.get('created_by'),
            'platform_url': 'http://localhost:5000'
        }, project_id=task_data.get('project_id'))
    
    # NEW DEADLINE-RELATED METHODS
    def task_deadline_approaching(self, notification_data):
        """Trigger when a task deadline is approaching"""
        return self.trigger_workflow('task_deadline_approaching', {
            'task_id': notification_data.get('task_id'),
            'task_title': notification_data.get('task_title'),
            'task_description': notification_data.get('task_description'),
            'project_name': notification_data.get('project_name'),
            'project_id': notification_data.get('project_id'),
            'assigned_to': notification_data.get('assigned_to'),
            'assigned_user_email': notification_data.get('assigned_user_email'),
            'due_date': notification_data.get('due_date'),
            'days_until_deadline': notification_data.get('days_until_deadline'),
            'deadline_label': notification_data.get('deadline_label'),
            'priority': notification_data.get('priority'),
            'status': notification_data.get('status'),
            'dashboard_url': notification_data.get('dashboard_url'),
            'notification_type': 'deadline_warning',
            'urgency_level': self._get_urgency_level(notification_data.get('days_until_deadline', 0))
        }, project_id=notification_data.get('project_id'))
    
    def task_overdue(self, notification_data):
        """Trigger when a task is overdue"""
        return self.trigger_workflow('task_overdue', {
            'task_id': notification_data.get('task_id'),
            'task_title': notification_data.get('task_title'),
            'task_description': notification_data.get('task_description'),
            'project_name': notification_data.get('project_name'),
            'project_id': notification_data.get('project_id'),
            'assigned_to': notification_data.get('assigned_to'),
            'assigned_user_email': notification_data.get('assigned_user_email'),
            'due_date': notification_data.get('due_date'),
            'days_overdue': notification_data.get('days_overdue'),
            'priority': 'urgent',
            'status': notification_data.get('status'),
            'dashboard_url': notification_data.get('dashboard_url'),
            'notification_type': 'overdue_alert',
            'escalation_required': notification_data.get('days_overdue', 0) > 3
        }, project_id=notification_data.get('project_id'))
    
    def project_deadline_approaching(self, project_data, days_until_deadline):
        """Trigger when project deadline is approaching"""
        return self.trigger_workflow('project_deadline_approaching', {
            'project_id': project_data.get('id'),
            'project_name': project_data.get('name'),
            'client_name': project_data.get('client_name'),
            'due_date': project_data.get('due_date'),
            'days_until_deadline': days_until_deadline,
            'progress': project_data.get('progress', 0),
            'total_tasks': project_data.get('total_tasks', 0),
            'completed_tasks': project_data.get('completed_tasks', 0),
            'pending_tasks': project_data.get('pending_tasks', 0),
            'owner': project_data.get('owner'),
            'dashboard_url': f"http://localhost:5000/project/{project_data.get('id')}",
            'urgency_level': self._get_urgency_level(days_until_deadline)
        }, project_id=project_data.get('id'))
    
    def task_completed(self, task_data):
        """Trigger when a task is completed"""
        return self.trigger_workflow('task_completed', {
            'task_id': task_data.get('id'),
            'task_title': task_data.get('title'),
            'project_name': task_data.get('project_name'),
            'assigned_to': task_data.get('assigned_to'),
            'completed_at': datetime.utcnow().isoformat(),
            'was_on_time': task_data.get('was_on_time', True),
            'completion_time': task_data.get('completion_time')
        }, project_id=task_data.get('project_id'))
    
    def project_completed(self, project_data):
        """Trigger when a project is completed"""
        return self.trigger_workflow('project_completed', {
            'project_id': project_data.get('id'),
            'project_name': project_data.get('name'),
            'client_name': project_data.get('client_name'),
            'completed_at': datetime.utcnow().isoformat(),
            'total_tasks': project_data.get('total_tasks', 0),
            'duration_days': project_data.get('duration_days', 0),
            'was_on_time': project_data.get('was_on_time', True)
        }, project_id=project_data.get('id'))
    
    def _get_urgency_level(self, days_until):
        """Get urgency level based on days until deadline"""
        if days_until <= 0:
            return 'critical'
        elif days_until <= 1:
            return 'urgent'
        elif days_until <= 3:
            return 'high'
        elif days_until <= 7:
            return 'medium'
        else:
            return 'low'

# Create singleton instance
n8n_service = N8NService()