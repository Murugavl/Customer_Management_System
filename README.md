# Flask Customer Management System

A web-based application for managing customer data using Flask, a lightweight Python web framework. This project provides features to add, edit, delete, and view customer information, making it ideal for small businesses and organizations.

---

## Features

- **Customer Management**: Add, edit, delete, and view customer details.
- **Responsive Design**: Works seamlessly on desktops, tablets, and mobile devices.
- **Secure**: Implements basic authentication and data validation.
- **Database Integration**: Uses MongoDB for data storage.

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- [Python 3.7+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Murugavl/Flask-Customer_Management_System.git
   cd Flask-Customer_Management_System
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000` to access the application.

---

## Project Structure

```
Flask-Customer_Management_System/
├── app/
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   ├── create_customer.html 
│   ├── home.html
│   ├── login.html
│   └── update_amount.html
|   └── view_all_customers.html
└── app.py                
```

---

## Usage

1. **Add a Customer**: Use the "Add Customer" button to input customer details.
2. **Delete a Customer**: Click the "Delete" button to remove a customer.
3. **View All Customers**: The homepage lists all customers with their details.

---

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Tailwind
- **Database**: MongoDB

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch-name`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch-name`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or support, please contact:

- **Author**: Murugavl
- **Email**: [vmv2k05@gmail.com](mailto:your-email@example.com)
- **GitHub**: [https://github.com/Murugavl](https://github.com/Murugavl)

---

## Screenshots

Include screenshots of the application in action (if available):

1. **Homepage**
   ![Homepage](/static/img/home_page.png)

2. **Customers Page**
   ![Customers](/static/img/customers_page.png)

---

