from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# This will be initialized in app.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'admin' or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True)
    email_templates = db.relationship('EmailTemplate', backref='creator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_employee(self):
        return self.role == 'employee'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='active')
    due_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)  # ADD THIS LINE
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='project', lazy=True, cascade='all, delete-orphan')
    automation_triggers = db.relationship('AutomationTrigger', backref='project', lazy=True)
    
    def get_progress(self):
        """Calculate project progress based on completed tasks"""
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return 0
        completed_tasks = len([task for task in self.tasks if task.status == 'completed'])
        return int((completed_tasks / total_tasks) * 100)
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='todo')  # 'todo', 'in_progress', 'completed'
    assigned_to = db.Column(db.String(100))
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def mark_complete(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return self.due_date < datetime.utcnow().date()
        return False
    
    def __repr__(self):
        return f'<Task {self.title}>'

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    spend = db.Column(db.Float, default=0.0)
    revenue = db.Column(db.Float, default=0.0)
    record_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_roi(self):
        """Calculate Return on Investment"""
        if self.spend > 0:
            return ((self.revenue - self.spend) / self.spend) * 100
        return 0
    
    def calculate_conversion_rate(self):
        """Calculate conversion rate percentage"""
        if self.clicks > 0:
            return (self.conversions / self.clicks) * 100
        return 0
    
    def __repr__(self):
        return f'<Analytics Project:{self.project_id} Date:{self.record_date}>'

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    template_type = db.Column(db.String(50))  # 'welcome', 'follow_up', 'newsletter', etc.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class AutomationTrigger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trigger_name = db.Column(db.String(200), nullable=False)
    trigger_type = db.Column(db.String(50), nullable=False)  # 'project_created', 'task_completed', etc.
    n8n_webhook_url = db.Column(db.String(500))
    trigger_data = db.Column(db.Text)  # JSON data for the trigger
    is_active = db.Column(db.Boolean, default=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationTrigger {self.trigger_name}>'
    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    email = db.Column(db.String(120))
    sector = db.Column(db.String(100))  # business sector
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with projects
    projects = db.relationship('Project', backref='client', lazy=True)
    
    def __repr__(self):
        return f'<Client {self.name}>'