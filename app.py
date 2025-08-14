# app.py - Updated with proper reports integration

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
login_manager = LoginManager()

def create_app():
    # Explicitly set template folder
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///marketing_platform.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # IMPORTANT: Enable development mode for auto-reload
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Initialize extensions with app
    from models import db
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Import models
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.homepage import homepage_bp
    from routes.clients import clients_bp
    from routes.n8n_webhooks import n8n_bp
    from routes.users import users_bp
    from routes.deadline_api import deadline_api
    from routes.reports import reports_bp  # ✅ Make sure this import is here

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(homepage_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(n8n_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(deadline_api)
    app.register_blueprint(reports_bp)  # ✅ Make sure this is registered

    
    @app.route('/auth/login')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html')
    
    @app.route('/simple-dashboard')
    @login_required
    def simple_dashboard():
        return render_template('simple_dashboard.html')
    
    from models import User, Client, Project, Task
    from sqlalchemy import desc, func
    from datetime import datetime, timedelta, date

    

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Enhanced dashboard with deadline information"""
        
        # Get all the data for the dashboard
        stats = get_dashboard_stats()
        recent_projects = get_recent_projects()
        recent_tasks = get_recent_tasks()
        
        # NEW: Get deadline information
        deadline_info = get_deadline_summary()
        
        return render_template('dashboard/index.html',
                            stats=stats,
                            recent_projects=recent_projects,
                            recent_tasks=recent_tasks,
                            deadline_info=deadline_info)

    # Helper functions for dashboard data
    def get_dashboard_stats():
        """Get overall statistics for the dashboard"""
        stats = {
            'clients': Client.query.count(),
            'projects': Project.query.count(),
            'tasks': Task.query.filter_by(status='pending').count(),
            'users': User.query.count()
        }
        
        # NEW: Add deadline-related stats
        today = date.today()
        stats.update({
            'overdue_tasks': Task.query.filter(
                Task.due_date < today,
                Task.status != 'completed'
            ).count(),
            'due_soon': Task.query.filter(
                Task.due_date.between(today, today + timedelta(days=7)),
                Task.status != 'completed'
            ).count()
        })
        
        return stats

    def get_recent_projects(limit=5):
        """Get recent projects ordered by creation date"""
        try:
            recent_projects = Project.query.join(Client).order_by(desc(Project.created_at)).limit(limit).all()
            return recent_projects
        except Exception as e:
            print(f"Error getting recent projects: {e}")
            return Project.query.order_by(desc(Project.created_at)).limit(limit).all()

    def get_recent_tasks(limit=10):
        """Get recent tasks ordered by creation date"""
        try:
            recent_tasks = Task.query.join(Project).outerjoin(User, Task.assigned_to == User.username).order_by(desc(Task.created_at)).limit(limit).all()
            return recent_tasks
        except Exception as e:
            print(f"Error getting recent tasks: {e}")
            return Task.query.order_by(desc(Task.created_at)).limit(limit).all()
    
    def get_deadline_summary():
        """NEW: Get deadline summary for dashboard"""
        try:
            today = date.today()
            tomorrow = today + timedelta(days=1)
            next_week = today + timedelta(days=7)
            
            # Base query for user's tasks
            base_query = Task.query.filter(Task.status != 'completed')
            
            # Filter by user permissions
            if not current_user.is_admin():
                base_query = base_query.join(Project).filter(
                    db.or_(
                        Project.user_id == current_user.id,
                        Task.assigned_to == current_user.username
                    )
                )
            
            deadline_summary = {
                'overdue': base_query.filter(Task.due_date < today).count(),
                'due_today': base_query.filter(Task.due_date == today).count(),
                'due_tomorrow': base_query.filter(Task.due_date == tomorrow).count(),
                'due_this_week': base_query.filter(
                    Task.due_date.between(today, next_week)
                ).count(),
                'recent_overdue_tasks': base_query.filter(
                    Task.due_date < today
                ).order_by(Task.due_date).limit(5).all()
            }
            
            return deadline_summary
            
        except Exception as e:
            print(f"Error getting deadline summary: {e}")
            return {
                'overdue': 0,
                'due_today': 0,
                'due_tomorrow': 0,
                'due_this_week': 0,
                'recent_overdue_tasks': []
            }
    
    @app.route('/project/<int:project_id>')
    @login_required
    def project_details(project_id):
        return render_template('project/details.html', project_id=project_id)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app



if __name__ == '__main__':
    app = create_app()
    
    # Run with debug mode and auto-reload
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=True,
        use_debugger=True,
        threaded=True
    )