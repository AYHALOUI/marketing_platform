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
    from routes.homepage import homepage_bp  # ADD THIS
    from routes.clients import clients_bp  # ADD THIS


    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(homepage_bp)  # ADD THIS
    app.register_blueprint(clients_bp)  # ADD THIS


    @app.route('/debug/users')
    def debug_users():
        from models import User
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': str(user.created_at)
            })
        return {'users': user_list, 'count': len(users)}


    
    @app.route('/auth/login')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html')
    
    from models import User, Client, Project, Task
    from sqlalchemy import desc, func
    from datetime import datetime, timedelta

    def get_dashboard_stats():
        """Get overall statistics for the dashboard"""
        stats = {
            'clients': Client.query.count(),
            'projects': Project.query.count(),
            'tasks': Task.query.filter_by(status='pending').count(),  # Only pending tasks
            'users': User.query.count()
        }
        return stats

    def get_recent_projects(limit=5):
        """Get recent projects ordered by creation date"""
        recent_projects = Project.query.join(Client).order_by(desc(Project.created_at)).limit(limit).all()
        return recent_projects

    def get_recent_tasks(limit=10):
        """Get recent tasks ordered by creation date"""
        recent_tasks = Task.query.join(Project).join(User, Task.assigned_to_id == User.id, isouter=True).order_by(desc(Task.created_at)).limit(limit).all()
        return recent_tasks

    def get_project_stats():
        """Get project statistics breakdown"""
        project_stats = {
            'total': Project.query.count(),
            'active': Project.query.filter_by(status='active').count(),
            'completed': Project.query.filter_by(status='completed').count(),
            'pending': Project.query.filter_by(status='pending').count()
        }
        return project_stats

    def get_task_stats():
        """Get task statistics breakdown"""
        task_stats = {
            'total': Task.query.count(),
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'completed': Task.query.filter_by(status='completed').count()
        }
        return task_stats

    def get_tasks_by_priority():
        """Get tasks grouped by priority"""
        priority_stats = {
            'high': Task.query.filter_by(priority='high').count(),
            'medium': Task.query.filter_by(priority='medium').count(),
            'low': Task.query.filter_by(priority='low').count()
        }
        return priority_stats

    # Updated dashboard route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard with comprehensive statistics and recent items"""
        
        # Get all the data for the dashboard
        stats = get_dashboard_stats()
        recent_projects = get_recent_projects()
        recent_tasks = get_recent_tasks()
        project_stats = get_project_stats()
        task_stats = get_task_stats()
        priority_stats = get_tasks_by_priority()
        
        return render_template('dashboard/index.html',
                            stats=stats,
                            recent_projects=recent_projects,
                            recent_tasks=recent_tasks,
                            project_stats=project_stats,
                            task_stats=task_stats,
                            priority_stats=priority_stats)

    # Alternative minimal version if you want to start simple
    @app.route('/dashboard')
    @login_required
    def dashboard_simple():
        """Simplified dashboard route"""
        
        # Basic stats
        stats = {
            'clients': Client.query.count(),
            'projects': Project.query.count(),
            'tasks': Task.query.filter_by(status='pending').count(),
            'users': User.query.count()
        }
        
        # Recent items
        recent_projects = Project.query.order_by(desc(Project.created_at)).limit(5).all()
        recent_tasks = Task.query.order_by(desc(Task.created_at)).limit(10).all()
        
        return render_template('dashboard/index.html',
                            stats=stats,
                            recent_projects=recent_projects,
                            recent_tasks=recent_tasks)
    
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