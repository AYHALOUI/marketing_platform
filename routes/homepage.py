from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Client

homepage_bp = Blueprint('homepage', __name__, url_prefix='/')

@homepage_bp.route('/')
def homepage():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Get all clients from database
    clients = Client.query.all()
    return render_template('homepage/index.html', clients=clients)