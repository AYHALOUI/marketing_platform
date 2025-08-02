# simple_test.py - Just test if reminders work

import requests

# CHANGE THIS TO YOUR EMAIL
your_email = "ahaloui@tm-holding.ma"

# N8N webhook URL
webhook_url = "http://localhost:5678/webhook/task_reminder"

def test_reminder():
    print("🧪 Testing simple reminder...")
    
    # Test data
    data = {
        "task_title": "Complete website design",
        "user_email": your_email,
        "due_date": "Tomorrow",
        "days_until": 1,
        "project_name": "Test Project",
        "task_url": "http://localhost:5000"
    }
    
    try:
        print(f"📤 Sending reminder to: {your_email}")
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Check your email")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure N8N is running on localhost:5678")

if __name__ == "__main__":
    print("📧 CHANGE YOUR EMAIL FIRST!")
    print(f"Current email: {your_email}")
    
    if your_email == "your-email@example.com":
        print("❌ Please update 'your_email' in the script first!")
    else:
        test_reminder()