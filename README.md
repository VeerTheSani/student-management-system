# 🎓 Student Management System

A simple full-stack web application to manage students and their academic results with CSV upload support, dashboards, automatic CGPA calculation, and an integrated AI Academic Assistant.

---

## 🚀 Features

* 📂 Upload students & results via CSV
* 🎯 Automatic total, percentage & CGPA calculation
* 👨‍🎓 Student Dashboard & 👩‍🏫 Teacher Dashboard
* 🔐 Authentication (JWT-based)
* 📁 MVC Architecture
* 🤖 **NEW:** AI-Powered Academic Assistant (Groq API) to analyze student performance

---

## 🛠 Tech Stack

* **Backend:** Node.js, Express.js
* **AI Microservice:** Python, FastAPI
* **AI Model:** Groq API (LLaMA 3)
* **Database:** MongoDB
* **Frontend:** EJS, CSS (Tailwind)
* **Other:** Multer (file upload), CSV Parser

---

## 📂 Project Structure

```text
student-management-system/
 ├── chatbot/               # Python FastAPI AI Server
 │   ├── chatbot.py
 │   ├── requirements.txt
 │   └── .env (Add Your GROQ API Here)
 ├── server/                # Node.js Express Backend
 │   ├── controller/
 │   ├── database/
 │   ├── middleware/
 │   ├── model/
 │   └── routes/
 ├── views/                 # EJS Frontend
 │   ├── student/
 │   ├── teacher/
 │   └── include/
 ├── Server.js
 ├── package.json

---

## ⚙️ How to Run This Project Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/NandaniJS08/student-management-system.git
cd student-management-system
```

---

### 2️⃣ Install Dependencies

```bash
npm install
```

---

### 3️⃣ Create `.env` File

Create a `.env` file in the root directory and add:

```env
PORT=3000
MONGO_URI=mongodb://localhost:27017/student_mgm2
JWT_SECRET=your_secret_key
```
also edit in /chatbot file, add Your Groq api in `.env`file
---

### 4️⃣ Start MongoDB

Make sure MongoDB is running on your system.

---

### 5️⃣ Run the Server

```bash
node Server.js
```

---

### 6️⃣ Open in Browser

```
http://localhost:3000
```

---

## 🧪 Sample Usage

1. Upload student data using CSV file given in repo
2. Upload result data using CSV file given in repo
3. View dashboards for analysis

---

## 📈 Future Improvements

* 📊 Add charts & analytics dashboard
* 🤖 Agentic AI implementation
* 🌐 Deploy to cloud (Render / Vercel)
* 📱 Improve UI/UX

---

## 👩‍💻 Author

**Nandani J Solgama**


---

## ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub!
