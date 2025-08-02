# routes/reports.py - Simplified version

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Project, Task, Client, User, db
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
import random

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def reports_dashboard():
    """Simple reports dashboard page"""
    return render_template('reports/index.html')

@reports_bp.route('/api/stats')
@login_required
def get_reports_stats():
    """API endpoint to get simplified report statistics"""
    try:
        # Get filter parameters
        days = request.args.get('days', 30, type=int)
        client_filter = request.args.get('client', 'all')
        
        print(f"📊 Generating reports for {days} days, client: {client_filter}")
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get basic project and client data
        projects = Project.query.all()
        clients = Client.query.all()
        tasks = Task.query.all()
        
        # Calculate key metrics
        total_projects = len(projects)
        completed_projects = len([p for p in projects if p.status == 'completed'])
        active_projects = len([p for p in projects if p.status == 'active'])
        total_clients = len(clients)
        
        # Calculate estimated revenue (since you don't have revenue tracking yet)
        estimated_revenue = total_projects * 15000  # $15k average per project
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        
        # Generate monthly trend data (simulated for now)
        monthly_labels = []
        monthly_revenue = []
        monthly_projects = []
        
        for i in range(6):  # Last 6 months
            month_date = datetime.now() - timedelta(days=30 * i)
            monthly_labels.insert(0, month_date.strftime('%b %Y'))
            # Simulate increasing revenue and projects over time
            base_revenue = 20000 + (i * 5000) + random.randint(-3000, 3000)
            base_projects = 2 + i + random.randint(0, 2)
            monthly_revenue.insert(0, base_revenue)
            monthly_projects.insert(0, base_projects)
        
        # Client distribution
        client_distribution = []
        for client in clients[:8]:  # Top 8 clients
            project_count = len([p for p in projects if p.client_id == client.id])
            if project_count > 0:
                client_distribution.append({
                    'name': client.name,
                    'count': project_count
                })
        
        # Project performance data
        project_performance = []
        for project in projects:
            # Simulate budget and ROI data
            budget = random.randint(10000, 50000)
            roi = random.randint(150, 400)
            
            project_performance.append({
                'id': project.id,
                'name': project.name,
                'client': project.client.name if project.client else 'No Client',
                'status': project.status,
                'progress': project.get_progress(),
                'budget': budget,
                'roi': roi,
                'created_at': project.created_at.isoformat()
            })
        
        # Sort by ROI descending
        project_performance.sort(key=lambda x: x['roi'], reverse=True)
        
        # Build response
        response_data = {
            'overview': {
                'total_revenue': estimated_revenue,
                'completed_projects': completed_projects,
                'active_projects': active_projects,
                'total_clients': total_clients,
                'completion_rate': round(completion_rate, 1),
                'task_completion_rate': 85.5,  # Simulated
                'avg_delivery_days': 18.5,  # Simulated
                'client_satisfaction': 94.2  # Simulated
            },
            'revenue_trends': {
                'labels': monthly_labels,
                'revenue': monthly_revenue,
                'projects': monthly_projects
            },
            'client_distribution': client_distribution,
            'project_performance': project_performance[:20],  # Top 20 projects
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'filters_applied': {
                'days': days,
                'client': client_filter
            }
        }
        
        print(f"✅ Reports data generated successfully")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error generating reports: {str(e)}")
        return jsonify({
            'error': 'Failed to generate reports',
            'details': str(e)
        }), 500

@reports_bp.route('/api/clients')
@login_required
def get_clients_for_filter():
    """Get clients for filter dropdown"""
    try:
        clients = Client.query.all()
        
        clients_data = []
        for client in clients:
            project_count = Project.query.filter_by(client_id=client.id).count()
            if project_count > 0:  # Only include clients with projects
                clients_data.append({
                    'id': client.id,
                    'name': client.name,
                    'project_count': project_count
                })
        
        return jsonify({
            'clients': clients_data,
            'count': len(clients_data)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting clients: {str(e)}")
        return jsonify({
            'error': 'Failed to get clients',
            'details': str(e)
        }), 500

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    """Export reports as PDF (placeholder for server-side PDF generation)"""
    try:
        # This would be where you'd generate a server-side PDF
        # For now, we'll use client-side PDF generation
        return jsonify({
            'message': 'PDF export initiated',
            'note': 'Using client-side PDF generation'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to export PDF',
            'details': str(e)
        }), 500