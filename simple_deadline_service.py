# simple_deadline_service.py - Simple email reminder service

import requests
import json
from datetime import datetime, date, timedelta
from app import create_app
from models import Task, User, Project, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDeadlineService:
    def __init__(self):
        self.n8n_webhook_url = "http://localhost:5678/webhook/task_reminder"
        self.app = create_app()
    
    def send_task_reminder(self, task_id: int) -> bool:
        """Send email reminder for a specific task"""
        with self.app.app_context():
            try:
                # Get task data
                task = Task.query.get(task_id)
                if not task or not task.due_date:
                    logger.error(f"Task {task_id} not found or has no due date")
                    return False
                
                # Get user email
                user = User.query.filter_by(username=task.assigned_to).first()
                if not user:
                    logger.error(f"User {task.assigned_to} not found")
                    return False
                
                # Calculate days until due
                today = date.today()
                days_until = (task.due_date - today).days
                
                # Prepare email data
                email_data = {
                    "task_title": task.title,
                    "user_email": user.email,
                    "due_date": task.due_date.strftime('%B %d, %Y'),
                    "days_until": days_until,
                    "project_name": task.project.name,
                    "task_url": f"http://localhost:5000/project/{task.project.id}"
                }
                
                # Send to N8N webhook
                response = requests.post(
                    self.n8n_webhook_url,
                    json=email_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Email reminder sent for task: {task.title} → {user.email}")
                    return True
                else:
                    logger.error(f"❌ N8N webhook failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error sending reminder: {str(e)}")
                return False
    
    def check_upcoming_deadlines(self, days_ahead: int = 3) -> int:
        """Check for tasks due in the next X days and send reminders"""
        with self.app.app_context():
            try:
                today = date.today()
                target_date = today + timedelta(days=days_ahead)
                
                # Find tasks due in the next X days
                upcoming_tasks = Task.query.filter(
                    Task.due_date.between(today, target_date),
                    Task.status != 'completed'
                ).all()
                
                logger.info(f"📅 Found {len(upcoming_tasks)} tasks due in next {days_ahead} days")
                
                sent_count = 0
                for task in upcoming_tasks:
                    if self.send_task_reminder(task.id):
                        sent_count += 1
                
                logger.info(f"📧 Sent {sent_count} email reminders")
                return sent_count
                
            except Exception as e:
                logger.error(f"❌ Error checking deadlines: {str(e)}")
                return 0
    
    def check_overdue_tasks(self) -> int:
        """Check for overdue tasks and send alerts"""
        with self.app.app_context():
            try:
                today = date.today()
                
                # Find overdue tasks
                overdue_tasks = Task.query.filter(
                    Task.due_date < today,
                    Task.status != 'completed'
                ).all()
                
                logger.info(f"🚨 Found {len(overdue_tasks)} overdue tasks")
                
                sent_count = 0
                for task in overdue_tasks:
                    # Send reminder for overdue tasks too
                    if self.send_task_reminder(task.id):
                        sent_count += 1
                
                logger.info(f"📧 Sent {sent_count} overdue alerts")
                return sent_count
                
            except Exception as e:
                logger.error(f"❌ Error checking overdue tasks: {str(e)}")
                return 0

def main():
    """Run deadline checks"""
    print("🚀 Simple Deadline Email Service")
    print("=" * 40)
    
    service = SimpleDeadlineService()
    
    # Check upcoming deadlines (next 3 days)
    upcoming_count = service.check_upcoming_deadlines(days_ahead=3)
    
    # Check overdue tasks
    overdue_count = service.check_overdue_tasks()
    
    print(f"✅ Completed: {upcoming_count} upcoming, {overdue_count} overdue")

if __name__ == "__main__":
    main()