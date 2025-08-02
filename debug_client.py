# debug_client.py - Check what the API is returning

from app import create_app
from models import Project, Client, db

def check_api_response():
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING PROJECT API RESPONSE")
        print("=" * 40)
        
        # Get project 1
        project = Project.query.get(1)
        if not project:
            print("❌ Project 1 not found")
            return
        
        print(f"📁 Project: {project.name}")
        print(f"🔢 Client ID: {project.client_id}")
        
        # Check if client exists
        if project.client_id:
            client = Client.query.get(project.client_id)
            if client:
                print(f"✅ Client found: {client.name}")
                print(f"   Company: {client.company}")
                print(f"   Email: {client.email}")
                print(f"   Sector: {client.sector}")
            else:
                print(f"❌ Client ID {project.client_id} not found in database")
        else:
            print("❌ No client_id assigned to project")
            
            # Let's assign one
            client = Client.query.first()
            if client:
                print(f"📋 Found client: {client.name}")
                project.client_id = client.id
                db.session.commit()
                print(f"✅ Assigned client {client.name} to project")
            else:
                print("📋 No clients exist. Creating one...")
                client = Client(
                    name="Nike",
                    company="Nike Inc.", 
                    email="marketing@nike.com",
                    sector="Sports & Fashion"
                )
                db.session.add(client)
                db.session.flush()
                
                project.client_id = client.id
                db.session.commit()
                print(f"✅ Created and assigned client: {client.name}")
        
        # Now check what the API endpoint returns
        print(f"\n🔧 CHECKING API ENDPOINT...")
        
        # Simulate the API call
        if project.client:
            print(f"✅ project.client exists:")
            print(f"   Name: {project.client.name}")
            print(f"   Company: {project.client.company}")
        else:
            print(f"❌ project.client is None - relationship issue!")
            
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Refresh your browser")
        print(f"2. Check browser console for errors")
        print(f"3. Look for client info on page")

if __name__ == "__main__":
    check_api_response()