Absolutely — here is a **clean, professional, GitHub-ready `README.md`** for your SmartDues project.

👉 **You can copy-paste the entire block below in one go.**
It fully documents everything we built up to Day 6 + frontend progress.

---

# ✅ **SMARTDUES — Bill Tracker & Reminder System**

*A full-stack personal finance app built with FastAPI, SQLite, React, TailwindCSS*

---

## 📌 Overview

**SmartDues** is a simple but powerful bill-tracking system that helps users manage:

* Monthly bills
* EMIs & recurring payments
* Upcoming due dates
* Payment history
* Dashboard summaries
* Automatic reminders (coming soon)

The project is being built step-by-step from scratch using **Python (FastAPI)** for backend and **React + Vite + TailwindCSS** for frontend.

---

## 📚 Tech Stack

### 🔹 **Backend**

* FastAPI
* SQLite (dev.db)
* SQLAlchemy ORM
* JWT Authentication
* Python 3.10+
* APScheduler (for reminders, upcoming)
* SendGrid + Twilio (planned)

### 🔹 **Frontend**

* React (Vite + TypeScript)
* Axios
* React Router
* TailwindCSS
* Custom CSS theme

---

# 🚀 Features Implemented (Till Day 6)

## **DAY 1 — Authentication**

* Signup (`/auth/signup`)
* Login (`/auth/login`)
* JWT token creation + verification
* Bcrypt password hashing
* Users stored in SQLite

---

## **DAY 2 — Bills CRUD**

Endpoints:

* `GET /bills`
* `POST /bills`
* `GET /bills/{bill_id}`
* `PUT /bills/{bill_id}`
* `DELETE /bills/{bill_id}`

Bill model includes:

* title
* amount
* due_date
* type (emi/other)
* repeat_interval
* reminder_days
* notes
* is_paid

---

## **DAY 3 — Dashboard API**

`GET /dashboard` returns:

* `total_month_unpaid`
* `upcoming_next_7_days`
* `overdue_count`

Used by frontend Dashboard page.

---

## **DAY 4 — Mark Bill Paid**

`POST /bills/{bill_id}/mark_paid`

When a bill is marked paid:

* `is_paid = True`
* If `repeat_interval == "monthly"` →
  **automatically generate next month’s bill**

---

## **DAY 5 — Recurring Bills Engine**

Smart month addition:

* Handles Feb 28/29 issues
* Preserves day when possible
* Auto-creates next bill with:

  * same amount
  * same title
  * same reminder_days
  * next-month due_date

---

## **DAY 6 — Payments Table**

New table created:

| Column  | Type      |
| ------- | --------- |
| id      | int       |
| user_id | int       |
| bill_id | int (opt) |
| amount  | float     |
| method  | string    |
| notes   | string    |
| paid_on | datetime  |

Whenever a bill is marked paid:
✔ auto-create payment record

Upcoming:

* `/payments/export?month=YYYY-MM`
* `/payments` page on frontend

---

# 🎨 Frontend Progress

## **Framework**

* React + TypeScript
* Vite
* TailwindCSS

## **Pages Implemented**

* Login page
* Dashboard (styled with hero section, cards, glass effect)
* Bills page (WIP)
* Debug page (for testing APIs)

## **Theme**

A custom CSS theme added in `index.css` provides:

* gradients
* glass cards
* colorful buttons
* modern UI components
* responsive layout

Screenshot used in hero banner:
`sandbox:/mnt/data/49c2c780-1083-435b-9a38-3db6401c9364.png`

## **Dashboard Features**

* Calls `/dashboard` on mount
* Auto-refresh when bills are updated:

```js
window.dispatchEvent(new Event("bills:updated"))
```

* Beautiful hero section
* Summary cards (total unpaid, upcoming, overdue)
* Upcoming bills list

---

# 📁 Project Structure

```
backend/
 ├── main.py
 ├── crud.py
 ├── models.py
 ├── schemas.py
 ├── scheduler.py
 ├── notify.py

frontend/
 ├── src/
 │    ├── api/client.ts
 │    ├── components/Navbar.tsx
 │    ├── pages/
 │    │    ├── Login.tsx
 │    │    ├── Dashboard.tsx
 │    │    ├── Bills.tsx
 │    │    ├── Debug.tsx
 │    ├── index.css
 ├── package.json
 ├── vite.config.ts
```

---

# 🧪 Running the Project

## **Backend**

```
cd backend
uvicorn main:app --reload
```

Runs on:

```
http://127.0.0.1:8000
```

Docs:

```
http://127.0.0.1:8000/docs
```

---

## **Frontend**

```
cd frontend
npm install
npm run dev
```

Runs on:

```
http://localhost:5173
```

---

# 📌 Next Planned Tasks

### 🔜 **Day 7+ Roadmap**

* Add Bill form (modal or page)
* Bills listing UI (pretty)
* Mark Paid button on frontend
* Payment history UI
* Settings page (notification preferences)
* WhatsApp/SMS/Email reminders
* PWA mode (Installable)
* Deploy to cloud (Render/Fly.io/Vercel)
* Convert to mobile app (Flutter/React Native)

---

# 📧 Contact / Notes

This repo is actively developed step-by-step.
Notifications (SMS/WhatsApp/email) will be added later when Twilio/SendGrid keys are configured.

---

