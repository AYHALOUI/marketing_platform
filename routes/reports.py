# routes/reports.py - Create this new file

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Project, Task, Client, User, db
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def reports_dashboard():
    """Main reports dashboard page"""
    return render_template('reports/index.html')

@reports_bp.route('/api/stats')
@login_required
def get_reports_stats():
    """API endpoint to get report statistics"""
    try:
        # Get filter parameters
        days = request.args.get('days', 30, type=int)
        client_filter = request.args.get('client')
        status_filter = request.args.get('status')
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Base queries
        projects_query = Project.query
        tasks_query = Task.query
        
        # Apply filters
        if client_filter and client_filter != 'all':
            projects_query = projects_query.join(Client).filter(Client.name.ilike(f'%{client_filter}%'))
            tasks_query = tasks_query.join(Project).join(Client).filter(Client.name.ilike(f'%{client_filter}%'))
        
        if status_filter and status_filter != 'all':
            projects_query = projects_query.filter(Project.status == status_filter)
            tasks_query = tasks_query.join(Project).filter(Project.status == status_filter)
        
        # Calculate key metrics
        total_projects = projects_query.count()
        completed_projects = projects_query.filter(Project.status == 'completed').count()
        active_projects = projects_query.filter(Project.status == 'active').count()
        
        total_tasks = tasks_query.count()
        completed_tasks = tasks_query.filter(Task.status == 'completed').count()
        pending_tasks = tasks_query.filter(Task.status.in_(['todo', 'in_progress'])).count()
        
        # Calculate completion rate
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Simulate revenue data (in a real app, you'd have a revenue table)
        estimated_revenue = total_projects * 15000  # $15k average per project
        
        # Get client distribution
        client_stats = db.session.query(
            Client.name,
            func.count(Project.id).label('project_count')
        ).join(Project).group_by(Client.name).all()
        
        # Get recent project performance
        recent_projects = projects_query.order_by(desc(Project.created_at)).limit(10).all()
        
        project_performance = []
        for project in recent_projects:
            # Simulate budget and spend data
            budget = 25000  # Default budget
            spent = budget * 0.8  # 80% spent on average
            roi = 250 + (project.id * 30)  # Simulated ROI
            
            project_performance.append({
                'id': project.id,
                'name': project.name,
                'client': project.client.name if project.client else 'No Client',
                'budget': budget,
                'spent': spent,
                'roi': roi,
                'status': project.status,
                'progress': project.get_progress(),
                'created_at': project.created_at.isoformat()
            })
        
        # Get team performance
        team_stats = []
        users = User.query.all()
        for user in users:
            user_projects = Project.query.filter_by(user_id=user.id).count()
            user_tasks = Task.query.filter_by(assigned_to=user.username).count()
            completed_user_tasks = Task.query.filter_by(
                assigned_to=user.username, 
                status='completed'
            ).count()
            
            completion_rate = (completed_user_tasks / user_tasks * 100) if user_tasks > 0 else 0
            
            team_stats.append({
                'username': user.username,
                'role': user.role,
                'projects': user_projects,
                'tasks': user_tasks,
                'completed_tasks': completed_user_tasks,
                'completion_rate': round(completion_rate, 1)
            })
        
        return jsonify({
            'overview': {
                'total_revenue': estimated_revenue,
                'completed_projects': completed_projects,
                'active_projects': active_projects,
                'completion_rate': round(completion_rate, 1),
                'task_completion_rate': round(task_completion_rate, 1),
                'avg_delivery_days': 18.5,  # Simulated
                'client_satisfaction': 94.2  # Simulated
            },
            'client_distribution': [
                {'name': stat.name, 'count': stat.project_count} 
                for stat in client_stats
            ],
            'project_performance': project_performance,
            'team_performance': team_stats,
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/revenue-trends')
@login_required
def get_revenue_trends():
    """Get revenue trends for charts"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Generate sample revenue data (in a real app, fetch from database)
        labels = []
        revenue_data = []
        project_data = []
        
        # Generate data for the last N days/months
        if days <= 30:
            # Daily data for last 30 days
            for i in range(days - 1, -1, -1):
                date_point = date.today() - timedelta(days=i)
                labels.append(date_point.strftime('%m/%d'))
                revenue_data.append(15000 + (i * 500) + (i % 3 * 2000))  # Simulated
                project_data.append(1 + (i % 4))  # Simulated
        else:
            # Monthly data
            months = min(12, days // 30)
            for i in range(months - 1, -1, -1):
                date_point = date.today() - timedelta(days=i * 30)
                labels.append(date_point.strftime('%b %Y'))
                revenue_data.append(45000 + (i * 5000) + (i % 3 * 10000))  # Simulated
                project_data.append(3 + (i % 5))  # Simulated
        
        return jsonify({
            'labels': labels,
            'revenue': revenue_data,
            'projects': project_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/export')
@login_required
def export_reports():
    """Export reports as PDF/CSV"""
    try:
        format_type = request.args.get('format', 'pdf')
        
        if format_type == 'pdf':
            # In a real app, generate PDF here
            return jsonify({
                'message': 'PDF export feature would be implemented here',
                'download_url': '/reports/download/reports.pdf'
            }), 200
        elif format_type == 'csv':
            # In a real app, generate CSV here
            return jsonify({
                'message': 'CSV export feature would be implemented here',
                'download_url': '/reports/download/reports.csv'
            }), 200
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500