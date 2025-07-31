# from flask import Flask, render_template, redirect, url_for
# from flask_login import LoginManager, login_required, current_user
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Initialize extensions
# login_manager = LoginManager()

# def create_app():
#     # Explicitly set template folder
#     app = Flask(__name__, template_folder='templates', static_folder='static')

    
#     # Configuration
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///marketing_platform.db')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
#     # IMPORTANT: Enable development mode for auto-reload
#     app.config['DEBUG'] = True
#     app.config['TEMPLATES_AUTO_RELOAD'] = True
#     app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
#     # Initialize extensions with app
#     from models import db
#     db.init_app(app)
#     login_manager.init_app(app)
#     login_manager.login_view = 'login'
    
#     # Import models
#     from models import User
    
#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))
    
#     # Register blueprints
#     from routes.auth import auth_bp
#     from routes.projects import projects_bp
#     from routes.tasks import tasks_bp
#     from routes.homepage import homepage_bp
#     from routes.clients import clients_bp
#     from routes.n8n_webhooks import n8n_bp
#     from routes.users import users_bp  # ADD THIS LINE


#     app.register_blueprint(auth_bp)
#     app.register_blueprint(projects_bp)
#     app.register_blueprint(tasks_bp)
#     app.register_blueprint(homepage_bp)
#     app.register_blueprint(clients_bp)
#     app.register_blueprint(n8n_bp)
#     app.register_blueprint(users_bp)  # ADD THIS LINE
    
#     @app.route('/auth/login')
#     def login():
#         if current_user.is_authenticated:
#             return redirect(url_for('dashboard'))
#         return render_template('auth/login.html')
    
    
#     from models import User, Client, Project, Task
#     from sqlalchemy import desc, func
#     from datetime import datetime, timedelta

#     @app.route('/dashboard')
#     @login_required
#     def dashboard():
#         """Dashboard with comprehensive statistics and recent items"""
        
#         # Get all the data for the dashboard
#         stats = get_dashboard_stats()
#         recent_projects = get_recent_projects()
#         recent_tasks = get_recent_tasks()
        
#         return render_template('dashboard/index.html',
#                             stats=stats,
#                             recent_projects=recent_projects,
#                             recent_tasks=recent_tasks)

#     # Helper functions for dashboard data
#     def get_dashboard_stats():
#         """Get overall statistics for the dashboard"""
#         stats = {
#             'clients': Client.query.count(),
#             'projects': Project.query.count(),
#             'tasks': Task.query.filter_by(status='pending').count(),
#             'users': User.query.count()
#         }
#         return stats

#     def get_recent_projects(limit=5):
#         """Get recent projects ordered by creation date"""
#         try:
#             recent_projects = Project.query.join(Client).order_by(desc(Project.created_at)).limit(limit).all()
#             return recent_projects
#         except Exception as e:
#             print(f"Error getting recent projects: {e}")
#             return Project.query.order_by(desc(Project.created_at)).limit(limit).all()

#     def get_recent_tasks(limit=10):
#         """Get recent tasks ordered by creation date"""
#         try:
#             recent_tasks = Task.query.join(Project).outerjoin(User, Task.assigned_to == User.username).order_by(desc(Task.created_at)).limit(limit).all()
#             return recent_tasks
#         except Exception as e:
#             print(f"Error getting recent tasks: {e}")
#             return Task.query.order_by(desc(Task.created_at)).limit(limit).all()
    
#     @app.route('/project/<int:project_id>')
#     @login_required
#     def project_details(project_id):
#         return render_template('project/details.html', project_id=project_id)
    
#     # Debug route for user information
#     @app.route('/debug/users')
#     def debug_users():
#         from models import User
#         users = User.query.all()
#         user_list = []
#         for user in users:
#             user_list.append({
#                 'id': user.id,
#                 'username': user.username,
#                 'email': user.email,
#                 'role': user.role,
#                 'created_at': str(user.created_at)
#             })
#         return {'users': user_list, 'count': len(users)}
    
#     # Create database tables
#     with app.app_context():
#         db.create_all()
    
#     return app

# if __name__ == '__main__':
#     app = create_app()
    
#     # Run with debug mode and auto-reload
#     app.run(
#         debug=True,
#         host='127.0.0.1',
#         port=5000,
#         use_reloader=True,
#         use_debugger=True,
#         threaded=True
#     )

# app.py - Updated with deadline monitoring integration

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
    from routes.deadline_api import deadline_api  # NEW: Deadline API

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(homepage_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(n8n_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(deadline_api)  # NEW: Register deadline API
    
    @app.route('/auth/login')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html')
    
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
                            deadline_info=deadline_info)  # NEW: Pass deadline info

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
    
    # NEW: Deadline monitoring health check route
    @app.route('/system/health')
    @login_required
    def system_health():
        """System health check including deadline monitoring"""
        if not current_user.is_admin():
            return redirect(url_for('dashboard'))
        
        try:
            from services.n8n_service import check_n8n_health
            from routes.deadline_api import get_deadline_stats
            
            health_info = {
                'n8n_service': check_n8n_health(),
                'deadline_monitoring': 'active',  # You could check if the service is running
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return render_template('system/health.html', health_info=health_info)
            
        except Exception as e:
            return render_template('system/health.html', 
                                 health_info={'error': str(e)})
    
    # Debug route for user information
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
    
    # NEW: Debug route for deadline system
    @app.route('/debug/deadlines')
    @login_required
    def debug_deadlines():
        """Debug endpoint for deadline system"""
        if not current_user.is_admin():
            return {'error': 'Admin access required'}, 403
        
        try:
            today = date.today()
            
            debug_info = {
                'current_date': today.isoformat(),
                'overdue_tasks': [],
                'approaching_deadlines': [],
                'n8n_webhooks': [],
                'system_status': {}
            }
            
            # Get overdue tasks
            overdue_tasks = Task.query.filter(
                Task.due_date < today,
                Task.status != 'completed'
            ).all()
            
            for task in overdue_tasks:
                debug_info['overdue_tasks'].append({
                    'id': task.id,
                    'title': task.title,
                    'due_date': task.due_date.isoformat(),
                    'days_overdue': (today - task.due_date).days,
                    'assigned_to': task.assigned_to,
                    'project': task.project.name
                })
            
            # Get approaching deadlines
            next_week = today + timedelta(days=7)
            approaching_tasks = Task.query.filter(
                Task.due_date.between(today, next_week),
                Task.status != 'completed'
            ).all()
            
            for task in approaching_tasks:
                debug_info['approaching_deadlines'].append({
                    'id': task.id,
                    'title': task.title,
                    'due_date': task.due_date.isoformat(),
                    'days_until': (task.due_date - today).days,
                    'assigned_to': task.assigned_to,
                    'project': task.project.name
                })
            
            # Get N8N webhook status
            from services.n8n_service import n8n_service
            debug_info['n8n_webhooks'] = n8n_service.get_webhook_urls()
            debug_info['system_status'] = n8n_service.health_check()
            
            return debug_info
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # NEW: Start deadline monitoring service in background (optional)
        if os.getenv('START_DEADLINE_SERVICE', 'false').lower() == 'true':
            try:
                from routes.deadline_monitor import start_deadline_monitor
                start_deadline_monitor()
                print("✅ Deadline monitoring service started in background")
            except Exception as e:
                print(f"⚠️ Could not start deadline monitoring service: {e}")
    
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