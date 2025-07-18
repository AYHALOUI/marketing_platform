# create_9_clients.py
from app import create_app
from models import db, Client
from datetime import datetime

def create_9_clients():
    app = create_app()
    
    with app.app_context():
        # Check if clients already exist
        existing_count = Client.query.count()
        if existing_count >= 9:
            print(f"✅ You already have {existing_count} clients in your database!")
            print("Here are your existing clients:")
            clients = Client.query.all()
            for client in clients:
                print(f"  • {client.name} ({client.company}) - {client.sector}")
            return
        
        print(f"📦 Found {existing_count} existing clients. Adding more...")
        
        # 9 diverse clients for marketing platform
        clients_data = [
            {
                'name': 'Tesla',
                'company': 'Tesla, Inc.',
                'email': 'marketing@tesla.com',
                'sector': 'Electric Vehicles & Energy'
            },
            {
                'name': 'Spotify',
                'company': 'Spotify Technology S.A.',
                'email': 'brand@spotify.com',
                'sector': 'Music Streaming'
            },
            {
                'name': 'Netflix',
                'company': 'Netflix, Inc.',
                'email': 'creative@netflix.com',
                'sector': 'Entertainment & Streaming'
            },
            {
                'name': 'Airbnb',
                'company': 'Airbnb, Inc.',
                'email': 'marketing@airbnb.com',
                'sector': 'Travel & Hospitality'
            },
            {
                'name': 'Starbucks',
                'company': 'Starbucks Corporation',
                'email': 'brand@starbucks.com',
                'sector': 'Food & Beverage'
            },
            {
                'name': 'Adobe',
                'company': 'Adobe Inc.',
                'email': 'creative@adobe.com',
                'sector': 'Software & Creative Tools'
            },
            {
                'name': 'Shopify',
                'company': 'Shopify Inc.',
                'email': 'partnerships@shopify.com',
                'sector': 'E-commerce Platform'
            },
            {
                'name': 'Zoom',
                'company': 'Zoom Video Communications',
                'email': 'marketing@zoom.us',
                'sector': 'Video Communications'
            },
            {
                'name': 'Peloton',
                'company': 'Peloton Interactive, Inc.',
                'email': 'brand@peloton.com',
                'sector': 'Fitness & Wellness'
            }
        ]
        
        print("\n🚀 Creating 9 awesome clients for your marketing platform...")
        
        created_count = 0
        for client_data in clients_data:
            # Check if client already exists
            existing = Client.query.filter_by(name=client_data['name']).first()
            if existing:
                print(f"  ⏭️  {client_data['name']} already exists, skipping...")
                continue
            
            # Create new client
            client = Client(
                name=client_data['name'],
                company=client_data['company'],
                email=client_data['email'],
                sector=client_data['sector']
            )
            
            try:
                db.session.add(client)
                db.session.flush()  # Get the ID without committing
                print(f"  ✅ Created {client_data['name']} ({client_data['sector']})")
                created_count += 1
                
            except Exception as e:
                print(f"  ❌ Error creating {client_data['name']}: {e}")
                db.session.rollback()
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} new clients!")
            
            # Show summary
            total_clients = Client.query.count()
            print(f"\n📊 Summary:")
            print(f"  • Total clients in database: {total_clients}")
            print(f"  • Clients created this run: {created_count}")
            
            print(f"\n📋 All your clients:")
            clients = Client.query.all()
            for i, client in enumerate(clients, 1):
                print(f"  {i}. {client.name} ({client.company}) - {client.sector}")
            
            print(f"\n✨ Your dashboard will now show {total_clients} clients!")
            print("🔄 Refresh your dashboard to see the new clients.")
            
        except Exception as e:
            print(f"❌ Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_9_clients()