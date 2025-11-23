# backend/schemas.py
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# --- auth / user ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone: Optional[str] = None

    class Config:
        orm_mode = True

# --- token ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- bill schemas ---
class BillBase(BaseModel):
    title: str
    amount: float
    due_date: date
    type: Optional[str] = "emi"
    repeat_interval: Optional[str] = None
    reminder_days: Optional[str] = None  # comma separated "7,3,1"
    notes: Optional[str] = None

class BillCreate(BillBase):
    pass

class BillUpdate(BaseModel):
    title: Optional[str]
    amount: Optional[float]
    due_date: Optional[date]
    type: Optional[str]
    repeat_interval: Optional[str]
    reminder_days: Optional[str]
    notes: Optional[str]
    is_paid: Optional[bool]

class BillOut(BillBase):
    id: int
    user_id: int
    is_paid: bool

    class Config:
        orm_mode = True


# --- payments schemas ---
class PaymentCreate(BaseModel):
    bill_id: Optional[int] = None
    amount: float
    method: Optional[str] = "manual"
    notes: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    user_id: int
    bill_id: Optional[int]
    amount: float
    method: Optional[str]
    paid_on: datetime
    notes: Optional[str]

    # Pydantic v2: allow reading attributes from ORM objects
    model_config = {
        "from_attributes": True
    }
