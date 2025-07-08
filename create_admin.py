from app import create_app
from models import User, db

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@marketing.com',
            role='admin'
        )
        admin.set_password('admin123')  # Change this password!
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Email: admin@marketing.com")
        except Exception as e:
            print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user()