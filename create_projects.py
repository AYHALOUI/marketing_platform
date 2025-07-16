from app import create_app
from models import db, User, Client, Project, Task
from datetime import datetime, date, timedelta
import random

def create_sample_projects():
    app = create_app()
    
    with app.app_context():
        # Get existing clients and users
        clients = Client.query.all()
        users = User.query.all()
        
        if not clients or not users:
            print("❌ No clients or users found. Please run seed_data.py first.")
            return
        
        # Sample projects for each client
        sample_projects = {
            'Nike': [
                {
                    'name': 'Nike Summer Campaign 2025',
                    'description': 'Comprehensive summer marketing campaign focusing on running and outdoor activities',
                    'status': 'active',
                    'days_ago': 45
                },
                {
                    'name': 'Nike Social Media Strategy',
                    'description': 'Instagram and TikTok engagement campaign targeting Gen Z athletes',
                    'status': 'active',
                    'days_ago': 30
                },
                {
                    'name': 'Nike Air Max Launch',
                    'description': 'Product launch campaign for new Air Max line',
                    'status': 'completed',
                    'days_ago': 75
                },
                {
                    'name': 'Nike Winter Collection',
                    'description': 'Cold weather gear marketing campaign',
                    'status': 'paused',
                    'days_ago': 20
                }
            ],
            'Coca-Cola': [
                {
                    'name': 'Coca-Cola Holiday Campaign',
                    'description': 'Christmas and New Year marketing campaign with festive themes',
                    'status': 'completed',
                    'days_ago': 60
                },
                {
                    'name': 'Coca-Cola Zero Sugar Launch',
                    'description': 'Product launch campaign for new zero sugar variant',
                    'status': 'active',
                    'days_ago': 25
                },
                {
                    'name': 'Coca-Cola Summer Refresh',
                    'description': 'Summer campaign focusing on refreshment and cooling',
                    'status': 'active',
                    'days_ago': 15
                }
            ],
            'Apple': [
                {
                    'name': 'iPhone 16 Launch Campaign',
                    'description': 'Global marketing campaign for iPhone 16 release',
                    'status': 'active',
                    'days_ago': 35
                },
                {
                    'name': 'Apple Watch Health Campaign',
                    'description': 'Health and fitness focused marketing for Apple Watch',
                    'status': 'active',
                    'days_ago': 40
                },
                {
                    'name': 'Apple Back to School',
                    'description': 'Educational discounts and student-focused marketing',
                    'status': 'completed',
                    'days_ago': 90
                },
                {
                    'name': 'Apple Vision Pro Demo',
                    'description': 'Experience campaign for Apple Vision Pro in retail stores',
                    'status': 'paused',
                    'days_ago': 10
                }
            ]
        }
        
        # Sample tasks for projects
        sample_tasks = [
            'Create social media content',
            'Design banner advertisements',
            'Develop email marketing campaign',
            'Plan influencer partnerships',
            'Create video advertisements',
            'Write blog content',
            'Design product packaging',
            'Coordinate photo shoots',
            'Develop landing page',
            'Create press release',
            'Plan event marketing',
            'Design print advertisements'
        ]
        
        print("🚀 Creating sample projects...")
        
        # Create projects for each client
        for client in clients:
            if client.name in sample_projects:
                client_projects = sample_projects[client.name]
                
                print(f"\n📁 Creating projects for {client.name}:")
                
                for proj_data in client_projects:
                    # Check if project already exists
                    existing = Project.query.filter_by(
                        name=proj_data['name'],
                        client_id=client.id
                    ).first()
                    
                    if existing:
                        print(f"  ⏭️  Project '{proj_data['name']}' already exists")
                        continue
                    
                    # Create project with backdated creation time
                    creation_date = datetime.utcnow() - timedelta(days=proj_data['days_ago'])
                    
                    # Calculate due date (30-90 days from creation)
                    due_date = creation_date + timedelta(days=random.randint(30, 90))
                    
                    project = Project(
                        name=proj_data['name'],
                        description=proj_data['description'],
                        status=proj_data['status'],
                        due_date=due_date.date(),
                        client_id=client.id,
                        user_id=random.choice(users).id,
                        created_at=creation_date
                    )
                    
                    db.session.add(project)
                    db.session.flush()  # Get project ID
                    
                    # Create 2-5 tasks for each project
                    task_count = random.randint(2, 5)
                    completed_tasks = 0
                    
                    for i in range(task_count):
                        task_name = random.choice(sample_tasks)
                        task_creation = creation_date + timedelta(days=random.randint(1, 10))
                        
                        # Determine task status based on project status
                        if proj_data['status'] == 'completed':
                            task_status = 'completed'
                            completed_tasks += 1
                        elif proj_data['status'] == 'active':
                            task_status = random.choice(['todo', 'in_progress', 'completed'])
                            if task_status == 'completed':
                                completed_tasks += 1
                        else:  # paused
                            task_status = random.choice(['todo', 'in_progress'])
                        
                        task = Task(
                            title=f"{task_name} - {client.name}",
                            description=f"Task for {proj_data['name']} project",
                            status=task_status,
                            assigned_to=random.choice(users).username,
                            due_date=(task_creation + timedelta(days=random.randint(7, 21))).date(),
                            project_id=project.id,
                            created_at=task_creation,
                            completed_at=task_creation + timedelta(days=random.randint(1, 14)) if task_status == 'completed' else None
                        )
                        
                        db.session.add(task)
                    
                    print(f"  ✅ Created '{proj_data['name']}' with {task_count} tasks")
        
        # Commit all changes
        db.session.commit()
        print("\n🎉 All sample projects created successfully!")
        
        # Print summary
        print("\n📊 Summary:")
        for client in clients:
            project_count = len(client.projects)
            active_count = len([p for p in client.projects if p.status == 'active'])
            completed_count = len([p for p in client.projects if p.status == 'completed'])
            
            print(f"  {client.name}: {project_count} projects ({active_count} active, {completed_count} completed)")

if __name__ == '__main__':
    create_sample_projects()