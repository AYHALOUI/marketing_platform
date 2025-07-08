from app import create_app
from models import User, db

def reset_database():
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@marketing.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        # Create test employee
        employee = User(
            username='sara',
            email='sara@marketing.com',
            role='employee'
        )
        employee.set_password('password123')
        
        try:
            db.session.add(admin)
            db.session.add(employee)
            db.session.commit()
            print("✅ Database reset successfully!")
            print("✅ Created admin user: admin/admin123")
            print("✅ Created employee user: sara/password123")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    reset_database()