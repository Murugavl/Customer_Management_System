from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")# Use a secure random key for session security

# MongoDB connection URI from environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in environment variables")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["customer_management"]
collection = db["customer"]
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
except Exception as e:
    raise RuntimeError(f"MongoDB connection failed: {e}")

# Load users from environment variables (You can extend this later as needed)
users = {
    "velmurugan": os.getenv("USER_VELMURUGAN_PASSWORD")  # This can be customized in the .env file
}

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            session['username'] = username  # Store user in session
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for('home'))  # Redirect to home or dashboard page
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user from session
    flash("You have logged out.", "success")
    return redirect(url_for('home'))

# Create Customer Route
@app.route('/create_customer', methods=['GET', 'POST'])
def create_customer():
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        name = request.form['name']
        phone = request.form['phone']
        date = request.form['date']
        try:
            amount_received = float(request.form['amount_received'])
        except ValueError:
            flash("Invalid amount received.", "danger")
            return redirect(url_for('create_customer'))

        balance_amount = request.form['balance_amount']

        address = request.form['address']
        model = request.form['model']

        # Check if customer ID already exists
        existing_customer = collection.find_one({"Id": customer_id})
        if existing_customer:
            flash(f"Customer ID {customer_id} already exists.", "danger")
            return redirect(url_for("view_all_customers"))
        else:
            customer = {
                "Id": customer_id,
                "Name": name,
                "Ph.no": phone,
                "Date": date,
                "Amount_Received": amount_received,
                "Balance_Amount": balance_amount,
                "Address": address,
                "Model": model
            }
            collection.insert_one(customer)
            flash(f"Customer {name} has been created.", "success")
            return redirect(url_for('view_all_customers'))

    return render_template('create_customer.html')

# View All Customers Route
@app.route('/view_all_customers', methods=['GET'])
def view_all_customers():
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    # Get the search query from the URL parameters
    search_query = request.args.get('search', '').strip()

    if search_query:
        # Query the database for customers whose name matches the search query
        customers = collection.find({"Name": {"$regex": search_query, "$options": "i"}})
    else:
        # If no search query, show all customers
        customers = collection.find()

    return render_template('view_all_customers.html', customers=customers, search_query=search_query)

# Update Amount Route
@app.route('/update_amount/<customer_id>', methods=['GET', 'POST'])
def update_amount(customer_id):
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    customer = collection.find_one({"Id": customer_id})
    
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('view_all_customers'))
    
    if request.method == 'POST':
        try:
            new_amount = float(request.form['new_amount'])
        except ValueError:
            flash("Invalid amount entered.", "danger")
            return redirect(url_for('update_amount', customer_id=customer_id))


        # Update the Amount Received and Balance Amount
        updated_received = customer["Amount_Received"] + new_amount
        updated_balance = float(customer["Balance_Amount"]) - new_amount

        if updated_balance < 0:
            flash("Insufficient balance to update.", "danger")
            return redirect(url_for('view_all_customers'))

        collection.update_one({"Id": customer_id}, {
            "$set": {
                "Amount_Received": updated_received,
                "Balance_Amount": str(updated_balance)
            }
        })
        flash(f"Updated amount for customer {customer['Name']}.", "success")
        return redirect(url_for('view_all_customers'))
    
    return render_template('update_amount.html', customer=customer)

@app.route('/delete_customer/<customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    collection.delete_one({"Id": customer_id})
    flash(f"Customer {customer_id} has been deleted.", "success")
    return redirect(url_for('view_all_customers'))

@app.route('/edit_customer/<customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    # Fetch the customer data from the database
    customer = collection.find_one({"Id": customer_id})
    
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('view_all_customers'))

    if request.method == 'POST':
        # Only update editable fields: Name, Phone, Address, Model
        updated_name = request.form['name']
        updated_phone = request.form['phone']
        updated_address = request.form['address']
        updated_model = request.form['model']

        # Update the customer record
        collection.update_one({"Id": customer_id}, {
            "$set": {
                "Name": updated_name,
                "Ph.no": updated_phone,
                "Address": updated_address,
                "Model": updated_model
            }
        })

        flash(f"Customer {updated_name} has been updated.", "success")
        return redirect(url_for('view_all_customers'))

    return render_template('edit_customer.html', customer=customer)

if __name__ == '__main__':
    app.run(debug=True)
