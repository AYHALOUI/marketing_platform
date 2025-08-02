# test_deadline_timeline.py - Test the reminder timeline instantly

import requests
import json
from datetime import datetime, date, timedelta

def test_timeline_scenario():
    """Test all scenarios in the timeline without waiting days"""
    
    webhook_url = "http://localhost:5678/webhook/task_reminder"
    test_email = "your-email@example.com"  # Change this to your email
    
    # Test scenarios simulating the timeline
    scenarios = [
        {
            "name": "📧 1 DAY BEFORE (Wednesday)",
            "task_title": "Complete Nike Campaign Design",
            "days_until": 1,
            "due_date": "Tomorrow",
            "expected": "Should send normal reminder email"
        },
        {
            "name": "📧 DEADLINE DAY (Thursday)",
            "task_title": "Complete Nike Campaign Design", 
            "days_until": 0,
            "due_date": "Today",
            "expected": "Should send urgent 'due today' email"
        },
        {
            "name": "🚨 OVERDUE (Friday)",
            "task_title": "Complete Nike Campaign Design",
            "days_until": -1,
            "due_date": "Yesterday", 
            "expected": "Should send URGENT overdue email"
        },
        {
            "name": "🚨 2 DAYS OVERDUE",
            "task_title": "Complete Nike Campaign Design",
            "days_until": -2,
            "due_date": "2 days ago",
            "expected": "Should send CRITICAL overdue email"
        }
    ]
    
    print("🧪 TESTING DEADLINE REMINDER TIMELINE")
    print("=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Days until deadline: {scenario['days_until']}")
        print(f"   Expected: {scenario['expected']}")
        
        # Prepare test data
        test_data = {
            "task_title": scenario["task_title"],
            "user_email": test_email,
            "due_date": scenario["due_date"],
            "days_until": scenario["days_until"],
            "project_name": "Nike Summer Campaign",
            "task_url": "http://localhost:5000/project/1"
        }
        
        try:
            print(f"   📤 Sending test webhook...")
            response = requests.post(webhook_url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: Webhook received by N8N")
                print(f"   📬 Check your email for: {scenario['name']}")
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: Cannot connect to N8N at {webhook_url}")
            print(f"   💡 Make sure N8N is running and workflow is active")
            break
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        # Wait a bit between tests
        input("   ⏳ Press Enter to continue to next scenario...")
    
    print(f"\n🎯 TIMELINE TEST COMPLETE!")
    print(f"📧 Check your email ({test_email}) for all 4 reminder types")
    print(f"\nYou should have received:")
    print(f"  1. Normal reminder (1 day before)")
    print(f"  2. Urgent reminder (due today)")  
    print(f"  3. Overdue alert (1 day late)")
    print(f"  4. Critical overdue (2+ days late)")

def test_real_task_creation():
    """Test by creating actual tasks with different due dates"""
    
    print("\n" + "=" * 50)
    print("🔧 ALTERNATIVE: TEST WITH REAL TASKS")
    print("=" * 50)
    
    # Create tasks with different due dates to test timeline
    today = date.today()
    
    test_tasks = [
        {
            "title": "Test Task - Due Tomorrow",
            "due_date": (today + timedelta(days=1)).isoformat(),
            "description": "This task should trigger '1 day before' reminder"
        },
        {
            "title": "Test Task - Due Today", 
            "due_date": today.isoformat(),
            "description": "This task should trigger 'due today' reminder"
        },
        {
            "title": "Test Task - Overdue",
            "due_date": (today - timedelta(days=1)).isoformat(),
            "description": "This task should trigger 'overdue' alert"
        }
    ]
    
    print("💡 To test with real tasks:")
    print("1. Go to your dashboard")
    print("2. Create these test tasks:")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n   Task {i}: {task['title']}")
        print(f"   Due Date: {task['due_date']}")
        print(f"   Purpose: {task['description']}")
    
    print(f"\n3. Run your deadline service:")
    print(f"   python simple_deadline_service.py")
    
    print(f"\n4. Check emails for reminders!")

if __name__ == "__main__":
    print("Choose testing method:")
    print("1. Quick webhook tests (instant)")
    print("2. Real task creation guide")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == "1":
        # Update email before testing
        print("\n🔧 IMPORTANT: Update your email in the script!")
        print("Change 'your-email@example.com' to your real email")
        input("Press Enter when ready...")
        test_timeline_scenario()
    elif choice == "2":
        test_real_task_creation()
    else:
        print("Invalid choice. Run the script again.")