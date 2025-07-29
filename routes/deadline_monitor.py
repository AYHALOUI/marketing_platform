# deadline_monitor.py - Create this file to monitor task deadlines

from app import create_app
from models import Task, User, Project, db
from services.n8n_service import n8n_service
from datetime import datetime, date, timedelta
import schedule
import time
import threading

class DeadlineMonitor:
    def __init__(self):
        self.app = create_app()
        
    def check_approaching_deadlines(self):
        """Check for tasks with approaching deadlines"""
        with self.app.app_context():
            try:
                print("🔍 Checking for approaching task deadlines...")
                
                # Get current date
                today = date.today()
                
                # Define deadline warning periods
                warning_periods = [
                    {'days': 1, 'label': 'tomorrow'},
                    {'days': 3, 'label': 'in 3 days'},
                    {'days': 7, 'label': 'in 1 week'}
                ]
                
                for period in warning_periods:
                    target_date = today + timedelta(days=period['days'])
                    
                    # Find tasks due on target date that are not completed
                    approaching_tasks = Task.query.filter(
                        Task.due_date == target_date,
                        Task.status != 'completed'
                    ).all()
                    
                    print(f"📅 Found {len(approaching_tasks)} tasks due {period['label']}")
                    
                    for task in approaching_tasks:
                        self.send_deadline_notification(task, period['days'], period['label'])
                
                # Check for overdue tasks
                self.check_overdue_tasks()
                
            except Exception as e:
                print(f"❌ Error checking deadlines: {str(e)}")
    
    def check_overdue_tasks(self):
        """Check for overdue tasks"""
        with self.app.app_context():
            try:
                today = date.today()
                
                # Find overdue tasks
                overdue_tasks = Task.query.filter(
                    Task.due_date < today,
                    Task.status != 'completed'
                ).all()
                
                print(f"⚠️ Found {len(overdue_tasks)} overdue tasks")
                
                for task in overdue_tasks:
                    days_overdue = (today - task.due_date).days
                    self.send_overdue_notification(task, days_overdue)
                    
            except Exception as e:
                print(f"❌ Error checking overdue tasks: {str(e)}")
    
    def send_deadline_notification(self, task, days_until, label):
        """Send notification for approaching deadline"""
        try:
            # Get assigned user
            assigned_user = User.query.filter_by(username=task.assigned_to).first()
            if not assigned_user:
                print(f"⚠️ User {task.assigned_to} not found for task {task.title}")
                return
            
            # Get project info
            project = task.project
            
            # Prepare notification data
            notification_data = {
                'type': 'deadline_approaching',
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'project_name': project.name,
                'project_id': project.id,
                'assigned_to': task.assigned_to,
                'assigned_user_email': assigned_user.email,
                'due_date': task.due_date.isoformat(),
                'days_until_deadline': days_until,
                'deadline_label': label,
                'status': task.status,
                'priority': self.get_task_priority(days_until),
                'dashboard_url': f'http://localhost:5000/project/{project.id}',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Trigger n8n workflow
            success = n8n_service.task_deadline_approaching(notification_data)
            
            if success:
                print(f"📧 Deadline notification sent for task: {task.title} (due {label})")
            else:
                print(f"❌ Failed to send deadline notification for task: {task.title}")
                
        except Exception as e:
            print(f"❌ Error sending deadline notification: {str(e)}")
    
    def send_overdue_notification(self, task, days_overdue):
        """Send notification for overdue task"""
        try:
            # Get assigned user
            assigned_user = User.query.filter_by(username=task.assigned_to).first()
            if not assigned_user:
                return
            
            # Get project info
            project = task.project
            
            # Prepare overdue notification data
            notification_data = {
                'type': 'task_overdue',
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'project_name': project.name,
                'project_id': project.id,
                'assigned_to': task.assigned_to,
                'assigned_user_email': assigned_user.email,
                'due_date': task.due_date.isoformat(),
                'days_overdue': days_overdue,
                'status': task.status,
                'priority': 'high',
                'dashboard_url': f'http://localhost:5000/project/{project.id}',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Trigger n8n workflow
            success = n8n_service.task_overdue(notification_data)
            
            if success:
                print(f"🚨 Overdue notification sent for task: {task.title} ({days_overdue} days overdue)")
            else:
                print(f"❌ Failed to send overdue notification for task: {task.title}")
                
        except Exception as e:
            print(f"❌ Error sending overdue notification: {str(e)}")
    
    def get_task_priority(self, days_until):
        """Determine task priority based on days until deadline"""
        if days_until <= 1:
            return 'urgent'
        elif days_until <= 3:
            return 'high'
        elif days_until <= 7:
            return 'medium'
        else:
            return 'low'
    
    def start_monitoring(self):
        """Start the deadline monitoring scheduler"""
        print("🚀 Starting deadline monitoring service...")
        
        # Schedule checks
        schedule.every().day.at("09:00").do(self.check_approaching_deadlines)  # Morning check
        schedule.every().day.at("17:00").do(self.check_approaching_deadlines)  # Evening check
        schedule.every().hour.do(self.check_overdue_tasks)  # Check overdue every hour
        
        # Run immediately on start
        self.check_approaching_deadlines()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run deadline check once (for testing)"""
        print("🔍 Running one-time deadline check...")
        self.check_approaching_deadlines()

def start_deadline_monitor():
    """Start deadline monitoring in a separate thread"""
    monitor = DeadlineMonitor()
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()
    return monitor

if __name__ == '__main__':
    # Run as standalone script
    monitor = DeadlineMonitor()
    
    # For testing, run once
    monitor.run_once()
    
    # For production, start continuous monitoring
    # monitor.start_monitoring()