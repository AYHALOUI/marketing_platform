# Create this file as services/n8n_service.py

import requests
import json
import os
from datetime import datetime
from models import AutomationTrigger, db

class N8NService:
    def __init__(self):
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook')
    
    def trigger_workflow(self, trigger_type, data, project_id=None):
        """
        Trigger an N8N workflow with specified data
        
        Args:
            trigger_type (str): Type of trigger ('client_created', 'project_created', etc.)
            data (dict): Data to send to N8N
            project_id (int): Optional project ID for tracking
        """
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
            
            print(f"🔄 Triggering N8N workflow: {trigger_type}")
            print(f"📡 Webhook URL: {webhook_endpoint}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                webhook_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ N8N workflow triggered successfully: {trigger_type}")
                
                # Log the trigger in database
                self._log_automation_trigger(trigger_type, payload, project_id, 'success')
                
                return True
            else:
                print(f"❌ N8N workflow failed: {response.status_code} - {response.text}")
                self._log_automation_trigger(trigger_type, payload, project_id, 'failed')
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"🔌 N8N connection error for {trigger_type}: {str(e)}")
            self._log_automation_trigger(trigger_type, data, project_id, 'connection_failed')
            return False
        except Exception as e:
            print(f"💥 Unexpected error triggering N8N workflow {trigger_type}: {str(e)}")
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
    
    # Specific workflow triggers
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
        """Trigger when a new task is created"""
        return self.trigger_workflow('task_created', {
            'task_id': task_data.get('id'),
            'task_title': task_data.get('title'),
            'project_name': task_data.get('project_name'),
            'assigned_to': task_data.get('assigned_to'),
            'due_date': task_data.get('due_date'),
            'status': task_data.get('status')
        }, project_id=task_data.get('project_id'))
    
    def task_completed(self, task_data):
        """Trigger when a task is completed"""
        return self.trigger_workflow('task_completed', {
            'task_id': task_data.get('id'),
            'task_title': task_data.get('title'),
            'project_name': task_data.get('project_name'),
            'assigned_to': task_data.get('assigned_to'),
            'completed_at': datetime.utcnow().isoformat()
        }, project_id=task_data.get('project_id'))
    
    def project_deadline_approaching(self, project_data, days_until_deadline):
        """Trigger when project deadline is approaching"""
        return self.trigger_workflow('project_deadline_approaching', {
            'project_id': project_data.get('id'),
            'project_name': project_data.get('name'),
            'client_name': project_data.get('client_name'),
            'due_date': project_data.get('due_date'),
            'days_until_deadline': days_until_deadline,
            'progress': project_data.get('progress', 0)
        }, project_id=project_data.get('id'))
    
    def project_completed(self, project_data):
        """Trigger when a project is completed"""
        return self.trigger_workflow('project_completed', {
            'project_id': project_data.get('id'),
            'project_name': project_data.get('name'),
            'client_name': project_data.get('client_name'),
            'completed_at': datetime.utcnow().isoformat(),
            'total_tasks': project_data.get('total_tasks', 0),
            'duration_days': project_data.get('duration_days', 0)
        }, project_id=project_data.get('id'))

# Create singleton instance
n8n_service = N8NService()