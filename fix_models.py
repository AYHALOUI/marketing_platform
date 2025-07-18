# Create this file as fix_models.py and run it to update your database

from app import create_app
from models import db, Project, Task

def fix_models():
    app = create_app()
    
    with app.app_context():
        try:
            # Add missing columns if they don't exist
            with db.engine.connect() as conn:
                
                # Check and add progress column to Project if missing
                try:
                    result = conn.execute("PRAGMA table_info(project)")
                    columns = [row[1] for row in result]
                    
                    if 'progress' not in columns:
                        print("Adding progress column to Project table...")
                        conn.execute("ALTER TABLE project ADD COLUMN progress INTEGER DEFAULT 0")
                        print("✅ Progress column added")
                    else:
                        print("✅ Progress column already exists")
                        
                except Exception as e:
                    print(f"Note: {e}")
                
                # Check and add priority column to Task if missing
                try:
                    result = conn.execute("PRAGMA table_info(task)")
                    columns = [row[1] for row in result]
                    
                    if 'priority' not in columns:
                        print("Adding priority column to Task table...")
                        conn.execute("ALTER TABLE task ADD COLUMN priority VARCHAR(10) DEFAULT 'medium'")
                        print("✅ Priority column added")
                    else:
                        print("✅ Priority column already exists")
                        
                    if 'assigned_to_id' not in columns:
                        print("Adding assigned_to_id column to Task table...")
                        conn.execute("ALTER TABLE task ADD COLUMN assigned_to_id INTEGER")
                        print("✅ assigned_to_id column added")
                    else:
                        print("✅ assigned_to_id column already exists")
                        
                except Exception as e:
                    print(f"Note: {e}")
                
                conn.commit()
                
            print("\n🎉 Database schema updated successfully!")
            print("Your dashboard should now work without errors.")
            
        except Exception as e:
            print(f"❌ Error updating database: {e}")

if __name__ == '__main__':
    fix_models()