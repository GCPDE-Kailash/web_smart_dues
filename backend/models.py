# backend/models.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    bills = relationship("Bill", back_populates="owner", cascade="all, delete-orphan")

class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(50), default="emi")  # emi, credit_card, rent, subscription, bill
    amount = Column(Numeric(12,2), nullable=False)
    due_date = Column(Date, nullable=False)
    repeat_interval = Column(String(20), nullable=True)  # monthly, yearly, none
    reminder_days = Column(String(100), nullable=True)  # e.g. "7,3,1"
    notes = Column(Text, nullable=True)
    is_paid = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("User", back_populates="bills")

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, Text, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.sql import func
# ... existing imports ...

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(12,2), nullable=False)
    method = Column(String(50), nullable=True)  # e.g., 'manual','razorpay','upi'
    paid_on = Column(TIMESTAMP, server_default=func.now())
    notes = Column(Text, nullable=True)

class ReminderLog(Base):
    __tablename__ = "reminders_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="SET NULL"))
    reminder_sent_at = Column(TIMESTAMP, nullable=True)
    channel = Column(String(20), nullable=True)
