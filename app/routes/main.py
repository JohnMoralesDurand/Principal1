from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal del sitio"""
    return render_template('index.html')

@main_bp.route('/home')
def home():
    """Redirección a la página principal"""
    return redirect(url_for('main.index'))
