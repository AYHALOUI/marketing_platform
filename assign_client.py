# assign_client.py - Make sure your project has a client

from app import create_app
from models import Project, Client, db

def assign_client_to_project():
    app = create_app()
    
    with app.app_context():
        print("🔍 CHECKING PROJECT 1...")
        
        # Get your project
        project = Project.query.get(1)
        if not project:
            print("❌ Project 1 not found")
            return
        
        print(f"📁 Project: {project.name}")
        print(f"🔢 Current client_id: {project.client_id}")
        
        # Check if it has a client
        if project.client_id:
            client = Client.query.get(project.client_id)
            if client:
                print(f"✅ Project already has client: {client.name} ({client.company})")
                return
        
        # No client assigned, let's assign one
        print("❌ No client assigned to this project")
        
        # Get first available client
        client = Client.query.first()
        if not client:
            print("📋 No clients exist. Creating a test client...")
            # Create a test client
            client = Client(
                name="Nike",
                company="Nike Inc.",
                email="marketing@nike.com",
                sector="Sports & Fashion"
            )
            db.session.add(client)
            db.session.flush()
            print(f"✅ Created client: {client.name}")
        
        # Assign client to project
        project.client_id = client.id
        db.session.commit()
        
        print(f"✅ SUCCESS!")
        print(f"   Project: {project.name}")
        print(f"   Client: {client.name} ({client.company})")
        print(f"   Sector: {client.sector}")
        print(f"\n🔄 Now refresh your browser page!")

if __name__ == "__main__":
    assign_client_to_project()