"""
Utility functions for validation and security
"""
import re
from functools import wraps
from flask import session, redirect, url_for, flash


def validate_phone(phone):
    """
    Validate phone number format
    Accepts formats: +91 98765 43210, 9876543210, +919876543210
    """
    if not phone:
        return False
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it matches common phone patterns
    pattern = r'^[\+]?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))


def validate_customer_id(customer_id):
    """
    Validate customer ID format
    Should be alphanumeric, 3-20 characters
    """
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
    Validate date format (YYYY-MM-DD)
    """
    if not date_string:
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_string))
