"""
Utility functions for validation and security
"""
import re
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash


def validate_phone(phone):

    if not phone:
        return False
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it matches common phone patterns
    pattern = r'^[\+]?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))


def validate_customer_id(customer_id):

    if not customer_id:
        return False
    
    pattern = r'^[A-Za-z0-9_-]{3,20}$'
    return bool(re.match(pattern, customer_id))


def validate_amount(amount):
    """
    Validate amount is a positive number
    """
    try:
        value = float(amount)
        return value >= 0
    except (ValueError, TypeError):
        return False


def validate_name(name):
    """
    Validate name contains only letters, spaces, and common punctuation
    """
    if not name or len(name) < 2 or len(name) > 100:
        return False
    
    pattern = r'^[A-Za-z\s\.\-\']+$'
    return bool(re.match(pattern, name))


def sanitize_input(text):
    """
    Sanitize text input by stripping whitespace and limiting length
    """
    if not text:
        return ""
    
    return text.strip()[:500]  # Limit to 500 characters


def login_required(f):
    """
    Decorator to require login for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_date(date_string):
    """
    Validate date is a real calendar date in YYYY-MM-DD format.
    Uses strptime so values like 2024-99-99 are correctly rejected.
    """
    if not date_string:
        return False
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False
