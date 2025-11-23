
# SmartDues — Web Backend (FastAPI + SQLite - MVP)

A simple, secure backend for **SmartDues**, a bill/dues/EMI tracking system built with **FastAPI**, **SQLite**, **JWT authentication**, and **SQLAlchemy**.

This backend is created step-by-step (Day 1 to Day 3) under a guided build plan.

---

## **📌 Table of Contents**

* [Project Overview](#project-overview)
* [Features Completed (Day 1–3)](#features-completed-day-1–3)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Setup Instructions](#setup-instructions)
* [Environment Variables](#environment-variables)
* [Running the Server](#running-the-server)
* [API Endpoints Summary](#api-endpoints-summary)
* [Testing Using Swagger](#testing-using-swagger)
* [Checking the SQLite Database](#checking-the-sqlite-database)
* [Git Workflow](#git-workflow)
* [Next Steps (Coming Day 4+)](#next-steps-coming-day-4)

---

# **📌 Project Overview**

SmartDues is a personal billing & reminders system that allows users to:

* Create and track bills / EMIs / credit card dues
* View upcoming payments
* Track unpaid dues for the current month
* View overdue bills
* Prepare for future recurring bill automation & notifications

This backend will later connect to:

* Web frontend (React)
* Mobile app (Flutter)

For now, it serves as a clean, secure API layer.

---

# **📌 Features Completed (Day 1–3)**

### **Day 1 — Project Setup**

✔ Created clean project structure
✔ Installed Python dependencies
✔ Added FastAPI, SQLAlchemy, JWT auth
✔ SQLite configured
✔ API running on `http://127.0.0.1:8000/docs`
✔ User Signup / Login (JWT) tested successfully

### **Day 2 — Bills CRUD**

✔ Added `/bills` endpoints
✔ Created sample bill
✔ Verified DB write using SQLite query
✔ GET /bills returning correct list

### **Day 3 — Dashboard Endpoint**

✔ Added monthly dues calculation
✔ Upcoming 7-days bills
✔ Overdue bills count
✔ `/dashboard` endpoint working

---

# **📌 Tech Stack**

### **Backend**

* FastAPI (Python)
* SQLAlchemy ORM
* SQLite (dev database)
* JWT Authentication (python-jose)
* Pydantic schemas

### **Tools**

* Uvicorn (ASGI server)
* Passlib (password hashing, pbkdf2_sha256)
* Alembic (migrations – planned)

---

# **📌 Project Structure**

```
smartdues_web/
│
├── backend/
│   ├── main.py            # FastAPI main entry
│   ├── auth.py            # JWT authentication + hashing
│   ├── crud.py            # Database operations
│   ├── database.py        # DB connection & Base metadata
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── dev.db             # SQLite database (auto-created)
│
├── requirements.txt
├── .env
└── README.md
```

---

# **📌 Setup Instructions**

### **1) Clone the project**

```
git clone <your-repo-url>
cd smartdues_web
```

### **2) Create & activate virtualenv**

```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1     (Windows PowerShell)
```

If PowerShell blocks script:

```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **3) Install dependencies**

```
pip install --upgrade pip
pip install -r ../requirements.txt
```

---

# **📌 Environment Variables**

Create a `.env` file in root:

```
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=super_secret_key_change_this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# **📌 Running the Server**

Inside `backend` folder with venv active:

```
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Now open Swagger UI:

👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# **📌 API Endpoints Summary**

### **Auth**

| Method | Endpoint       | Description          |
| ------ | -------------- | -------------------- |
| POST   | `/auth/signup` | Register user        |
| POST   | `/auth/login`  | Login, get JWT token |

### **Bills**

| Method | Endpoint      | Description      |
| ------ | ------------- | ---------------- |
| POST   | `/bills`      | Create a bill    |
| GET    | `/bills`      | List all bills   |
| GET    | `/bills/{id}` | Get bill details |
| PUT    | `/bills/{id}` | Update bill      |
| DELETE | `/bills/{id}` | Delete bill      |

### **Dashboard**

| Method | Endpoint     | Description                                          |
| ------ | ------------ | ---------------------------------------------------- |
| GET    | `/dashboard` | Monthly unpaid total, upcoming 7 days, overdue count |

---

# **📌 Testing Using Swagger**

1. Open `http://127.0.0.1:8000/docs`
2. **Signup** using `/auth/signup`
3. **Login** using `/auth/login`
4. Copy the `access_token`
5. Click **Authorize** → paste:

   ```
   Bearer <your_token>
   ```
6. Now test:

   * POST /bills
   * GET /bills
   * GET /dashboard

---

# **📌 Checking the SQLite Database**

Inside Python REPL:

```
python
```

Then:

```python
import sqlite3

conn = sqlite3.connect('dev.db')
cur = conn.cursor()

for row in cur.execute("SELECT id, user_id, title, amount, due_date, is_paid FROM bills"):
    print(row)

conn.close()
```

---

# **📌 Git Workflow**

```
git add .
git commit -m "Meaningful message here"
git push origin main
```

---

# **📌 Next Steps (Coming Day 4+)**

* Day 4: **Mark bill as paid** + (optional) auto-generate next recurring bill
* Day 5: **Update & delete** endpoints UI behavior
* Day 6: **Frontend setup (React + Vite + Tailwind)**
* Day 7: Connect frontend → backend
* Day 8–14: Build all frontend pages
* Week 3: Reminder engine (APScheduler) + email
* Week 4: Deployment (Render + Vercel)

---

If you want a **second version** of README (more concise or more detailed), or want to split into multiple files, tell me.

When ready, say **“Day4 start”** and I’ll give your next task.


Day 6 — Add payments table + record payment on mark-paid (step-by-step)
Goal (today):
Add a payments table/model.
When POST /bills/{id}/mark_paid is called, create a Payment record (amount, paid_on, method).
Add GET /payments to list payments for the current user.
Test via Swagger and verify in SQLite.

pip install APScheduler sendgrid twilio python-dotenv
python - <<'PY'
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
os.environ["SENDGRID_API_KEY"] = "SG.YOUR_KEY"
client = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
try:
    resp = client.send(Mail(from_email="no-reply@smartdues.test", to_emails="you@example.com", subject="Test", plain_text_content="test"))
    print("sent", resp.status_code)
except Exception as e:
    print("error", e)
PY
