# backend/crud.py
from sqlalchemy.orm import Session
from backend import models, schemas
from typing import List, Optional
from datetime import date

# --- user CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password_hash: str, phone: Optional[str] = None):
    user = models.User(email=email, password_hash=password_hash, phone=phone)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- bills CRUD ---
def create_bill(db: Session, user_id: int, bill_in: schemas.BillCreate):
    bill = models.Bill(
        user_id=user_id,
        title=bill_in.title,
        amount=bill_in.amount,
        due_date=bill_in.due_date,
        type=bill_in.type,
        repeat_interval=bill_in.repeat_interval,
        reminder_days=bill_in.reminder_days,
        notes=bill_in.notes,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

def get_bills_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Bill]:
    return db.query(models.Bill).filter(models.Bill.user_id == user_id).order_by(models.Bill.due_date).offset(skip).limit(limit).all()

def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()

def update_bill(db: Session, bill_id: int, data: dict):
    bill = get_bill(db, bill_id)
    if not bill:
        return None
    for key, value in data.items():
        setattr(bill, key, value)
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

def delete_bill(db: Session, bill_id: int):
    bill = get_bill(db, bill_id)
    if bill:
        db.delete(bill)
        db.commit()
    return bill

# add these imports at top of crud.py if not present
from datetime import date, timedelta
from sqlalchemy import func
from typing import List
import backend.models as models

def get_dashboard(db, user_id: int):
    """
    Return:
      - total_month_unpaid: sum of unpaid bills for current month (float)
      - upcoming_next_7_days: list of upcoming unpaid bills (dicts)
      - overdue_count: integer count of unpaid overdue bills
    """

    today = date.today()

    # calculate month start and next month start
    month_start = today.replace(day=1)
    if today.month == 12:
        next_month_start = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month_start = today.replace(month=today.month + 1, day=1)

    # total unpaid dues for current month (use coalesce to return 0 when sum is NULL)
    total_month = db.query(func.coalesce(func.sum(models.Bill.amount), 0))\
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date >= month_start,
            models.Bill.due_date < next_month_start
        ).scalar()

    # upcoming next 7 days (inclusive)
    next_7 = today + timedelta(days=7)
    upcoming_q = db.query(models.Bill)\
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date >= today,
            models.Bill.due_date <= next_7
        )\
        .order_by(models.Bill.due_date)

    upcoming = upcoming_q.all()

    # overdue count
    overdue_count = db.query(func.count(models.Bill.id))\
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date < today
        ).scalar()

    # normalize values for JSON
    try:
        total_month_val = float(total_month or 0)
    except Exception:
        # fallback if DB returns Decimal-like object
        total_month_val = float(str(total_month or 0))

    upcoming_list = []
    for b in upcoming:
        upcoming_list.append({
            "id": b.id,
            "title": b.title,
            "amount": float(b.amount),
            "due_date": b.due_date.isoformat() if b.due_date else None,
            "type": b.type,
            "is_paid": bool(b.is_paid)
        })

    return {
        "total_month_unpaid": total_month_val,
        "upcoming_next_7_days": upcoming_list,
        "overdue_count": int(overdue_count or 0)
    }
