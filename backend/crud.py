# backend/crud.py

from typing import List, Optional
from datetime import date, timedelta
import calendar

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend import models, schemas


# -------------------------------
# USER CRUD
# -------------------------------

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


# -------------------------------
# BILLS CRUD
# -------------------------------

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
    return (
        db.query(models.Bill)
        .filter(models.Bill.user_id == user_id)
        .order_by(models.Bill.due_date)
        .offset(skip)
        .limit(limit)
        .all()
    )

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


# -------------------------------
# RECURRING UTILS
# -------------------------------

def add_months(dt: date, months: int = 1) -> date:
    """
    Safely add months to a date (handles month overflow).
    Example: Jan 31 + 1 month -> Feb 28 (or 29)
    """
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# -------------------------------
# MARK BILL PAID + AUTO CREATE NEXT MONTH
# -------------------------------

def mark_bill_paid(db: Session, bill_id: int, user_id: int):
    bill = get_bill(db, bill_id)
    if not bill or bill.user_id != user_id:
        return None

    bill.is_paid = True
    db.add(bill)
    db.commit()
    db.refresh(bill)

    # Auto-create next recurring bill
    try:
        if bill.repeat_interval and bill.repeat_interval.lower() == "monthly":
            next_due = add_months(bill.due_date or date.today(), 1)

            new_bill = models.Bill(
                user_id=bill.user_id,
                title=bill.title,
                type=bill.type,
                amount=bill.amount,
                due_date=next_due,
                repeat_interval=bill.repeat_interval,
                reminder_days=bill.reminder_days,
                notes=bill.notes,
                is_paid=False,
            )
            db.add(new_bill)
            db.commit()
            db.refresh(new_bill)

    except Exception:
        pass  # swallow recurring errors

    # Record payment
    try:
        payment_amount = float(bill.amount)
    except Exception:
        payment_amount = bill.amount

    create_payment(
        db,
        user_id=bill.user_id,
        payment_in={
            "bill_id": bill.id,
            "amount": payment_amount,
            "method": "manual",
            "notes": "Marked paid via API",
        },
    )

    return bill


# -------------------------------
# PAYMENTS CRUD
# -------------------------------

def create_payment(db: Session, user_id: int, payment_in: dict):
    p = models.Payment(
        user_id=user_id,
        bill_id=payment_in.get("bill_id"),
        amount=payment_in.get("amount"),
        method=payment_in.get("method"),
        notes=payment_in.get("notes"),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def get_payments_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Payment)
        .filter(models.Payment.user_id == user_id)
        .order_by(models.Payment.paid_on.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# -------------------------------
# DASHBOARD
# -------------------------------

def get_dashboard(db, user_id: int):
    today = date.today()

    # Month boundaries
    month_start = today.replace(day=1)
    next_month_start = (
        today.replace(year=today.year + 1, month=1, day=1)
        if today.month == 12
        else today.replace(month=today.month + 1, day=1)
    )

    # total unpaid dues for current month
    total_month = (
        db.query(func.coalesce(func.sum(models.Bill.amount), 0))
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date >= month_start,
            models.Bill.due_date < next_month_start,
        )
        .scalar()
    )

    # upcoming 7 days
    next_7 = today + timedelta(days=7)
    upcoming = (
        db.query(models.Bill)
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date >= today,
            models.Bill.due_date <= next_7,
        )
        .order_by(models.Bill.due_date)
        .all()
    )

    # overdue count
    overdue_count = (
        db.query(func.count(models.Bill.id))
        .filter(
            models.Bill.user_id == user_id,
            models.Bill.is_paid == False,
            models.Bill.due_date < today,
        )
        .scalar()
    )

    # Convert for JSON
    upcoming_list = [
        {
            "id": b.id,
            "title": b.title,
            "amount": float(b.amount),
            "due_date": b.due_date.isoformat(),
            "type": b.type,
            "is_paid": bool(b.is_paid),
        }
        for b in upcoming
    ]

    return {
        "total_month_unpaid": float(total_month or 0),
        "upcoming_next_7_days": upcoming_list,
        "overdue_count": int(overdue_count or 0),
    }
