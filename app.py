from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Import configuration and utilities
from config import config
from utils import (
    validate_phone, validate_customer_id, validate_amount, 
    validate_name, validate_date, sanitize_input, login_required
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter (guards /login against brute-force attacks)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],          # no global limit — only apply where decorated
    storage_uri="memory://"
)

# Configure logging
# In production/Docker, log only to stdout so container orchestrators
# (Docker, Kubernetes) capture logs natively — no file needed or wanted.
# In development, also write to app.log for easy local inspection.
_log_handlers = [logging.StreamHandler()]
if app.config['DEBUG']:
    _log_handlers.append(logging.FileHandler('app.log'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_log_handlers
)
logger = logging.getLogger(__name__)

# MongoDB setup with error handling
try:
    client = MongoClient(
        app.config['MONGO_URI'],
        serverSelectionTimeoutMS=5000,
        maxPoolSize=50
    )
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
    
    db = client[app.config['DB_NAME']]
    collection = db[app.config['COLLECTION_NAME']]
    
    # Create indexes for better performance
    collection.create_index([("Id", ASCENDING)], unique=True)
    collection.create_index([("Name", ASCENDING)])
    collection.create_index([("Ph.no", ASCENDING)])
    collection.create_index([("Date", ASCENDING)])
    logger.info("Database indexes created successfully")
    
except ConnectionFailure as e:
    logger.error(f"MongoDB connection failed: {e}")
    raise RuntimeError(f"MongoDB connection failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error during MongoDB setup: {e}")
    raise RuntimeError(f"Database setup failed: {e}")

# Build the users table from environment.
# Preferred: set USER_PASSWORD_HASH to a pre-hashed value so the plaintext
# password never enters the process. Fall back to hashing USER_PASSWORD if
# only the plaintext is provided (legacy / first-run convenience).
_pw_hash = app.config.get('USER_PASSWORD_HASH') or generate_password_hash(app.config['USER_PASSWORD'])
users = {
    app.config['USER_NAME']: _pw_hash
}


# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page route"""
    logger.info("Home page accessed")
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 50 per hour")
def login():
    """Login route with password hashing"""
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        
        # Validate inputs
        if not username or not password:
            flash("Username and password are required.", "danger")
            logger.warning(f"Login attempt with missing credentials")
            return render_template('login.html')
        
        # Check credentials with hashed password
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            session.permanent = True
            flash(f"Welcome, {username}!", "success")
            logger.info(f"User '{username}' logged in successfully")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout route"""
    username = session.get('username', 'Unknown')
    session.pop('username', None)
    flash("You have logged out.", "success")
    logger.info(f"User '{username}' logged out")
    return redirect(url_for('home'))


@app.route('/create_customer', methods=['GET', 'POST'])
@login_required
def create_customer():
    """Create new customer with comprehensive validation"""
    if request.method == 'POST':
        try:
            # Get and sanitize form data
            customer_id = sanitize_input(request.form.get('customer_id', ''))
            name = sanitize_input(request.form.get('name', ''))
            phone = sanitize_input(request.form.get('phone', ''))
            date = sanitize_input(request.form.get('date', ''))
            amount_received = request.form.get('amount_received', '0')
            balance_amount = request.form.get('balance_amount', '0')
            address = sanitize_input(request.form.get('address', ''))
            model = sanitize_input(request.form.get('model', ''))
            
            # Validate all inputs
            validation_errors = []
            
            if not validate_customer_id(customer_id):
                validation_errors.append("Invalid Customer ID format (3-20 alphanumeric characters)")
            
            if not validate_name(name):
                validation_errors.append("Invalid name format")
            
            if not validate_phone(phone):
                validation_errors.append("Invalid phone number format")
            
            if not validate_date(date):
                validation_errors.append("Invalid date format")
            
            if not validate_amount(amount_received):
                validation_errors.append("Invalid amount received")
            
            if not validate_amount(balance_amount):
                validation_errors.append("Invalid balance amount")
            
            if not address or len(address) < 5:
                validation_errors.append("Address must be at least 5 characters")
            
            # If validation errors exist, show them
            if validation_errors:
                for error in validation_errors:
                    flash(error, "danger")
                logger.warning(f"Validation errors in create_customer: {validation_errors}")
                return redirect(url_for('create_customer'))
            
            # Convert amounts to float
            amount_received = float(amount_received)
            balance_amount = float(balance_amount)
            
            # Check if customer ID already exists
            existing_customer = collection.find_one({"Id": customer_id})
            if existing_customer:
                flash(f"Customer ID {customer_id} already exists.", "danger")
                logger.warning(f"Attempt to create duplicate customer ID: {customer_id}")
                return redirect(url_for("view_all_customers"))
            
            # Create customer document with audit fields
            now = datetime.now(timezone.utc)
            customer = {
                "Id": customer_id,
                "Name": name,
                "Ph.no": phone,
                "Date": date,
                "Amount_Received": amount_received,
                "Balance_Amount": balance_amount,
                "Address": address,
                "Model": model,
                "created_at": now,
                "created_by": session.get('username'),
                "updated_at": now,
                "updated_by": session.get('username')
            }
            
            collection.insert_one(customer)
            flash(f"Customer {name} has been created successfully.", "success")
            logger.info(f"Customer created: {customer_id} by {session.get('username')}")
            return redirect(url_for('view_all_customers'))
            
        except DuplicateKeyError:
            flash(f"Customer ID {customer_id} already exists.", "danger")
            logger.error(f"Duplicate key error for customer ID: {customer_id}")
            return redirect(url_for('create_customer'))
        except PyMongoError as e:
            flash("Database error occurred. Please try again.", "danger")
            logger.error(f"Database error in create_customer: {e}")
            return redirect(url_for('create_customer'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", "danger")
            logger.error(f"Unexpected error in create_customer: {e}")
            return redirect(url_for('create_customer'))
    
    return render_template('create_customer.html')


@app.route('/view_all_customers', methods=['GET'])
@login_required
def view_all_customers():
    """View all customers with pagination and search"""
    try:
        # Get search query and page number
        search_query = sanitize_input(request.args.get('search', ''))
        page = request.args.get('page', 1, type=int)
        per_page = app.config['CUSTOMERS_PER_PAGE']
        
        # Build query
        query = {}
        if search_query:
            # Escape user input before inserting into $regex to prevent
            # ReDoS via crafted patterns like (a+)+ causing catastrophic backtracking
            escaped = re.escape(search_query)
            query = {
                "$or": [
                    {"Name": {"$regex": escaped, "$options": "i"}},
                    {"Id": {"$regex": escaped, "$options": "i"}},
                    {"Ph.no": {"$regex": escaped, "$options": "i"}},
                    {"Model": {"$regex": escaped, "$options": "i"}}
                ]
            }
        
        # Get total count for pagination
        total_customers = collection.count_documents(query)
        total_pages = (total_customers + per_page - 1) // per_page
        
        # Get paginated results — materialized to list so the cursor is fully
        # consumed before rendering, and sorted for stable pagination across requests
        customers = list(
            collection.find(query)
            .sort("Name", ASCENDING)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        
        logger.info(f"Viewing customers page {page}, search: '{search_query}'")
        
        return render_template(
            'view_all_customers.html',
            customers=customers,
            search_query=search_query,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_customers=total_customers
        )
        
    except PyMongoError as e:
        flash("Error retrieving customer data.", "danger")
        logger.error(f"Database error in view_all_customers: {e}")
        return render_template('view_all_customers.html', customers=[], search_query='', page=1, total_pages=0, total_customers=0)
    except Exception as e:
        flash("An unexpected error occurred.", "danger")
        logger.error(f"Unexpected error in view_all_customers: {e}")
        return render_template('view_all_customers.html', customers=[], search_query='', page=1, total_pages=0, total_customers=0)


@app.route('/update_amount/<customer_id>', methods=['GET', 'POST'])
@login_required
def update_amount(customer_id):
    """Update customer payment amount"""
    try:
        customer = collection.find_one({"Id": customer_id})
        
        if not customer:
            flash("Customer not found.", "danger")
            logger.warning(f"Attempt to update non-existent customer: {customer_id}")
            return redirect(url_for('view_all_customers'))
        
        if request.method == 'POST':
            new_amount = request.form.get('new_amount', '0')
            
            # Validate amount
            if not validate_amount(new_amount):
                flash("Invalid amount entered.", "danger")
                return redirect(url_for('update_amount', customer_id=customer_id))
            
            new_amount = float(new_amount)
            
            # Update the Amount Received and Balance Amount
            updated_received = float(customer["Amount_Received"]) + new_amount
            updated_balance = float(customer["Balance_Amount"]) - new_amount
            
            if updated_balance < 0:
                flash("Payment amount exceeds balance.", "danger")
                logger.warning(f"Attempt to overpay for customer {customer_id}")
                return redirect(url_for('view_all_customers'))
            
            collection.update_one(
                {"Id": customer_id},
                {
                    "$set": {
                        "Amount_Received": updated_received,
                        "Balance_Amount": updated_balance,
                        "updated_at": datetime.now(timezone.utc),
                        "updated_by": session.get('username')
                    }
                }
            )
            
            flash(f"Updated payment for customer {customer['Name']}.", "success")
            logger.info(f"Amount updated for customer {customer_id} by {session.get('username')}")
            return redirect(url_for('view_all_customers'))
        
        return render_template('update_amount.html', customer=customer)
        
    except PyMongoError as e:
        flash("Database error occurred.", "danger")
        logger.error(f"Database error in update_amount: {e}")
        return redirect(url_for('view_all_customers'))
    except Exception as e:
        flash("An unexpected error occurred.", "danger")
        logger.error(f"Unexpected error in update_amount: {e}")
        return redirect(url_for('view_all_customers'))


@app.route('/delete_customer/<customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Delete customer record"""
    try:
        result = collection.delete_one({"Id": customer_id})
        
        if result.deleted_count > 0:
            flash(f"Customer {customer_id} has been deleted.", "success")
            logger.info(f"Customer {customer_id} deleted by {session.get('username')}")
        else:
            flash(f"Customer {customer_id} not found.", "danger")
            logger.warning(f"Attempt to delete non-existent customer: {customer_id}")
        
        return redirect(url_for('view_all_customers'))
        
    except PyMongoError as e:
        flash("Error deleting customer.", "danger")
        logger.error(f"Database error in delete_customer: {e}")
        return redirect(url_for('view_all_customers'))
    except Exception as e:
        flash("An unexpected error occurred.", "danger")
        logger.error(f"Unexpected error in delete_customer: {e}")
        return redirect(url_for('view_all_customers'))


@app.route('/edit_customer/<customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """Edit customer details"""
    try:
        customer = collection.find_one({"Id": customer_id})
        
        if not customer:
            flash("Customer not found.", "danger")
            logger.warning(f"Attempt to edit non-existent customer: {customer_id}")
            return redirect(url_for('view_all_customers'))
        
        if request.method == 'POST':
            # Get and sanitize form data
            updated_name = sanitize_input(request.form.get('name', ''))
            updated_phone = sanitize_input(request.form.get('phone', ''))
            updated_address = sanitize_input(request.form.get('address', ''))
            updated_model = sanitize_input(request.form.get('model', ''))
            
            # Validate inputs
            validation_errors = []
            
            if not validate_name(updated_name):
                validation_errors.append("Invalid name format")
            
            if not validate_phone(updated_phone):
                validation_errors.append("Invalid phone number format")
            
            if not updated_address or len(updated_address) < 5:
                validation_errors.append("Address must be at least 5 characters")
            
            if validation_errors:
                for error in validation_errors:
                    flash(error, "danger")
                logger.warning(f"Validation errors in edit_customer: {validation_errors}")
                return redirect(url_for('edit_customer', customer_id=customer_id))
            
            # Update the customer record
            collection.update_one(
                {"Id": customer_id},
                {
                    "$set": {
                        "Name": updated_name,
                        "Ph.no": updated_phone,
                        "Address": updated_address,
                        "Model": updated_model,
                        "updated_at": datetime.now(timezone.utc),
                        "updated_by": session.get('username')
                    }
                }
            )
            
            flash(f"Customer {updated_name} has been updated.", "success")
            logger.info(f"Customer {customer_id} updated by {session.get('username')}")
            return redirect(url_for('view_all_customers'))
        
        return render_template('edit_customer.html', customer=customer)
        
    except PyMongoError as e:
        flash("Database error occurred.", "danger")
        logger.error(f"Database error in edit_customer: {e}")
        return redirect(url_for('view_all_customers'))
    except Exception as e:
        flash("An unexpected error occurred.", "danger")
        logger.error(f"Unexpected error in edit_customer: {e}")
        return redirect(url_for('view_all_customers'))


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    flash("Page not found.", "danger")
    return redirect(url_for('home'))


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    flash("An internal error occurred. Please try again later.", "danger")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
