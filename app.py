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
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    
    # Basic routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/auth/login')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard/index.html')
    
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