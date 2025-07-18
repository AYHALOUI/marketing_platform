# Create this file as routes/n8n_webhooks.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

n8n_bp = Blueprint('n8n', __name__, url_prefix='/api/n8n')

@n8n_bp.route('/webhook/status', methods=['POST'])
def n8n_status_update():
    """
    Receive status updates from N8N workflows
    This endpoint receives callbacks when N8N workflows complete
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        workflow_id = data.get('workflow_id')
        status = data.get('status')  # 'success', 'failed', 'running'
        trigger_type = data.get('trigger_type')
        result_data = data.get('result_data', {})
        
        print(f"📨 N8N Status Update Received:")
        print(f"  Workflow ID: {workflow_id}")
        print(f"  Status: {status}")
        print(f"  Trigger Type: {trigger_type}")
        print(f"  Result: {json.dumps(result_data, indent=2)}")
        
        # Handle different workflow results
        if trigger_type == 'client_created' and status == 'success':
            # N8N successfully sent welcome email
            print(f"✅ Welcome email sent for client")
            
        elif trigger_type == 'task_created' and status == 'success':
            # N8N successfully notified assignee
            print(f"✅ Task notification sent")
            
        elif trigger_type == 'project_completed' and status == 'success':
            # N8N successfully generated and sent project report
            print(f"✅ Project completion report sent")
            
        # TODO: Update database with workflow results
        # You can store the results in AutomationTrigger table
        
        return jsonify({
            'message': 'Status update received',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing N8N status update: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@n8n_bp.route('/webhook/data', methods=['POST'])
def n8n_data_update():
    """
    Receive data updates from N8N workflows
    This can be used to update project/task data based on N8N workflow results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        update_type = data.get('update_type')
        entity_id = data.get('entity_id')
        update_data = data.get('update_data', {})
        
        print(f"📊 N8N Data Update Received:")
        print(f"  Update Type: {update_type}")
        print(f"  Entity ID: {entity_id}")
        print(f"  Update Data: {json.dumps(update_data, indent=2)}")
        
        # Handle different types of data updates
        if update_type == 'task_update':
            # Update task based on N8N workflow result
            from models import Task, db
            task = Task.query.get(entity_id)
            if task:
                # Example: Update task notes with N8N results
                task.description += f"\n\nN8N Update: {update_data.get('notes', '')}"
                db.session.commit()
                print(f"✅ Task {entity_id} updated with N8N data")
        
        elif update_type == 'project_metrics':
            # Update project metrics from external sources via N8N
            from models import Project, db
            project = Project.query.get(entity_id)
            if project:
                # You could store metrics in a separate table
                print(f"✅ Project {entity_id} metrics updated")
        
        return jsonify({
            'message': 'Data update processed',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing N8N data update: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@n8n_bp.route('/test', methods=['GET', 'POST'])
def test_n8n_connection():
    """
    Test endpoint to verify N8N integration is working
    """
    if request.method == 'POST':
        # Test outgoing webhook to N8N
        from services.n8n_service import n8n_service
        
        test_data = {
            'test': True,
            'message': 'Hello from Marketing Platform!',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        success = n8n_service.trigger_workflow('test_connection', test_data)
        
        return jsonify({
            'message': 'Test webhook sent to N8N',
            'success': success,
            'data': test_data
        }), 200
    
    else:
        # Test incoming webhook from N8N
        return jsonify({
            'message': 'N8N webhook endpoint is working!',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'ready'
        }), 200

@n8n_bp.route('/workflows', methods=['GET'])
@login_required
def get_active_workflows():
    """
    Get list of active N8N workflows for this platform
    """
    try:
        from models import AutomationTrigger
        
        triggers = AutomationTrigger.query.filter_by(is_active=True).all()
        
        workflows = []
        for trigger in triggers:
            workflows.append({
                'id': trigger.id,
                'name': trigger.trigger_name,
                'type': trigger.trigger_type,
                'webhook_url': trigger.n8n_webhook_url,
                'created_at': trigger.created_at.isoformat() if trigger.created_at else None,
                'project_id': trigger.project_id
            })
        
        return jsonify({
            'workflows': workflows,
            'count': len(workflows)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500