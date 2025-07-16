from app import create_app
from models import db, User, Client, Project
from datetime import datetime, date

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        
        sara = User(username='sara', email='sara@example.com', role='employee')
        sara.set_password('password123')
        
        # Create clients
        client1 = Client(
            name='Nike',
            company='Nike Inc.',
            email='contact@nike.com',
            sector='Sports & Fashion'
        )
        
        client2 = Client(
            name='Coca-Cola',
            company='The Coca-Cola Company',
            email='marketing@coca-cola.com',
            sector='Beverage'
        )
        
        client3 = Client(
            name='Apple',
            company='Apple Inc.',
            email='marketing@apple.com',
            sector='Technology'
        )
        
        # Add to database
        db.session.add(admin)
        db.session.add(sara)
        db.session.add(client1)
        db.session.add(client2)
        db.session.add(client3)
        db.session.commit()
        
        print("✅ Sample data created successfully!")
        print("Users: admin/admin123, sara/password123")
        print("Clients: Nike, Coca-Cola, Apple")

if __name__ == '__main__':
    seed_database()