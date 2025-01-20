from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure random key for session security

# MongoDB Atlas connection URI
MONGO_URI = "mongodb+srv://Murugavel:vvel2005@csm.nxtxr.mongodb.net/?retryWrites=true&w=majority&appName=CSM"

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["customer_management"]
collection = db["customer"]

# Dummy users for login, you can replace this with your actual users collection in MongoDB
users = {
    "admin": "password123"  # For example: admin password
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
        amount_received = float(request.form['amount_received'])
        balance_amount = request.form['balance_amount']
        address = request.form['address']
        model = request.form['model']

        # Check if customer ID already exists
        existing_customer = collection.find_one({"Id": customer_id})
        if existing_customer:
            flash(f"Customer ID {customer_id} already exists.", "danger")
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
@app.route('/view_all_customers')
def view_all_customers():
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    customers = collection.find()
    return render_template('view_all_customers.html', customers=customers)

# Update Amount Route
@app.route('/update_amount/<customer_id>', methods=['GET', 'POST'])
def update_amount(customer_id):
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    customer = collection.find_one({"Id": customer_id})
    if request.method == 'POST':
        new_amount = float(request.form['new_amount'])

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

# Delete Customer Route
@app.route('/delete_customer/<customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if 'username' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    collection.delete_one({"Id": customer_id})
    flash(f"Customer {customer_id} has been deleted.", "success")
    return redirect(url_for('view_all_customers'))

if __name__ == '__main__':
    app.run(debug=True)
