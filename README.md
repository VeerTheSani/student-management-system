# 🎓 Student Management System

A full-stack web application to manage students and their academic results with CSV upload support, dashboards, automatic CGPA calculation, and an integrated AI Academic Assistant powered by RAG (Retrieval-Augmented Generation).

---

## 🚀 Features

- 📂 Upload students & results via CSV
- 🎯 Automatic total, percentage & CGPA calculation
- 👨‍🎓 Student Dashboard & 👩‍🏫 Teacher Dashboard
- 🔐 Authentication (JWT-based)
- 📁 MVC Architecture
- 🤖 AI-Powered Academic Assistant (Groq API + LLaMA 3) to analyze student performance
- 🧠 RAG System (ChromaDB + Sentence Transformers) — AI answers from real academic documents
- 📄 Academic docs support: exam schedules, unit notes, guidelines, academic calendar

---

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Node.js, Express.js |
| AI Microservice | Python, FastAPI |
| AI Model | Groq API (LLaMA 3.3 70B) |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Database | MongoDB |
| Frontend | EJS, Tailwind CSS |
| Other | Multer, CSV Parser, Motor (async MongoDB) |

---

## 📂 Project Structure

```
student-management-system/
 ├── chatbot/                   # Python FastAPI AI Microservice
 │   ├── chatbot.py             # Main FastAPI app with /chatt and /tchatt endpoints
 │   ├── rag_setup.py           # RAG system: ChromaDB + embeddings
 │   ├── docs/                  # Academic documents (txt files for RAG)
 │   │   ├── exam_schedule.txt
 │   │   ├── academic_calendar.txt
 │   │   ├── student_guidelines.txt
 │   │   └── java_oop_notes.txt
 │   ├── chroma_store/          # Auto-generated vector database (do not edit)
 │   ├── requirements.txt
 │   └── .env                   # Add your GROQ_API_KEY here
 ├── server/                    # Node.js Express Backend
 │   ├── controller/
 │   ├── database/
 │   ├── middleware/
 │   ├── model/
 │   └── routes/
 ├── views/                     # EJS Frontend
 │   ├── student/
 │   ├── teacher/
 │   └── include/
 ├── Server.js
 └── package.json
```

---

## ⚙️ How to Run This Project Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/NandaniJS08/student-management-system.git
cd student-management-system
```

### 2️⃣ Install Node Dependencies

```bash
npm install
```

### 3️⃣ Install Python Dependencies

```bash
cd chatbot
pip install -r requirements.txt
```

> ⚠️ First run will download the embedding model (~80MB). Cached after that.

### 4️⃣ Create `.env` Files

Root `.env`:
```
PORT=3000
MONGO_URI=mongodb://localhost:27017/student_mgm2
JWT_SECRET=your_secret_key
```

`chatbot/.env`:
```
GROQ_API_KEY=your_groq_api_key
```

### 5️⃣ Start MongoDB

Make sure MongoDB is running on your system.

### 6️⃣ Run Both Servers

Terminal 1 — Node.js server:
```bash
node Server.js
```

Terminal 2 — Python AI microservice:
```bash
cd chatbot
uvicorn chatbot:app --reload
```

### 7️⃣ Open in Browser

```
http://localhost:3000
```

---

## 🧠 How the RAG System Works

```
docs/*.txt  →  chunked  →  embedded  →  stored in ChromaDB
                                               ↓
student asks question  →  question embedded  →  similar chunks found
                                               ↓
                              chunks injected into Groq prompt
                                               ↓
                              AI answers using your actual documents
```

To add new documents, just drop any `.txt` file inside `chatbot/docs/` and restart the Python server. It auto-loads everything.

---

## 🧪 Sample Usage

1. Upload student data using the CSV file provided in the repo
2. Upload result data using the CSV file provided in the repo
3. View dashboards for analysis
4. Ask the AI assistant about exam schedules, unit topics, attendance rules, or academic performance

---

## 📈 Future Improvements

- 📊 Charts & analytics dashboard
- 🤖 Agentic AI implementation
- 🌐 Deploy to cloud (Render / Vercel)
- 📱 Improved UI/UX
- 📎 Teacher document upload via portal

---

## 👩‍💻 Authors

- **Nandani J Solgama** — Node.js backend, frontend, database
- **Veer (VeerTheSani)** — AI microservice, RAG system, Groq API integration

---

## ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub!
