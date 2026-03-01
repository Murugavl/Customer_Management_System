# 🧾 Flask Customer Management System

A web-based **Customer Management System** built using **Flask**, designed to manage customer records, payment details, and service information.  
This application is suitable for small businesses and organizations and is **fully Dockerized** for easy and consistent deployment.

---

## ✨ Features

- **Customer Management**: Add, edit, delete, and view customer details
- **Payment Tracking**: Track received and balance amounts for each customer
- **Search Functionality**: Search customers by name
- **Authentication**: Basic login and session handling
- **Responsive Design**: Works on desktops, tablets, and mobile devices
- **Dark / Light Mode**: Theme toggle for better user experience
- **Database Integration**: Uses MongoDB for data storage
- **Docker Support**: Run the application anywhere using Docker

---

## 🚀 Getting Started

### ✅ Prerequisites

Ensure you have the following installed:

- Python **3.9+**
- Git
- Docker *(optional but recommended)*

---

## 🛠️ Installation (Without Docker)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Murugavl/Customer_Management_System.git
cd Customer_Management_System
```
### 2️⃣ Create & Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    
# Windows 
venv\Scripts\activate  
```
### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Create .env File

Create a .env file in the project root:
```bash
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
USER_NAME=your_user_name
USER_PASSWORD_HASH=your_hashed_password
```
> Generate your hash with:
> `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"`
### 5️⃣ Run the Application
```
python app.py
```

### 6️⃣ Open in Browser
```
http://127.0.0.1:5000
```
---
## 🐳 Running with Docker (Recommended)

### 🔹Option 1: Build & Run Locally
#### Build the Docker Image
```bash
docker build -t cms-app .
```

#### Run the Container
```bash
docker run -p 5000:5000 --env-file .env cms-app
```

#### Open in Browser
```bash
http://localhost:5000
```
### 🔹 Option 2: Run from Docker Hub
#### The image is publicly available on Docker Hub.
```bash
docker pull murugavl/cms-app:v1
docker run -p 5000:5000 --env-file .env murugavl/cms-app:v1
```
## 🧑‍💻 Usage
- Login using configured credentials.
- Add Customer: Enter customer and service details.
- View Customers: Browse all customer records.
- Update Amounts: Modify received and balance payments.
- Edit Customer: Update customer information.
- Delete Customer: Remove customer records.
- Toggle Theme: Switch between dark and light mode.

---
## 🧰 Technologies Used
- Backend: Flask (Python)
- Frontend: HTML, CSS, Tailwind CSS
- Database: MongoDB
- Server: Gunicorn
- Containerization: Docker

---
## 🔐 Security Notes
- Sensitive data managed using environment variables.
- .env file excluded using .dockerignore.
- Gunicorn used for production-ready serving.
---

## 🤝 Contributing

#### Contributions are welcome!
### Steps:
```bash
git checkout -b feature-branch-name
git commit -m "Add new feature"
git push origin feature-branch-name
```
#### Then open a Pull Request.
---

## 📄 License
This project is licensed under the MIT License.
See the LICENSE file for details.
---

## ⭐ Highlights
- Dockerized Flask application with MongoDB backend.
- Production-ready Docker image published to Docker Hub.
- Clean UI with dark/light mode support.
- Portable, scalable, and deployment-ready architecture.
---