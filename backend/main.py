# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend import database, schemas, crud, auth
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os

# Initialize DB
database.init_db()

app = FastAPI(title="SmartDues - Starter API")

# CORS - adjust origin in production
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth routes ---
@app.post("/auth/signup", response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(payload.password)
    user = crud.create_user(db, email=payload.email, password_hash=hashed, phone=payload.phone)
    return user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
    access_token = auth.create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- Bills routes ---
@app.post("/bills", response_model=schemas.BillOut)
def create_bill_route(bill_in: schemas.BillCreate, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bill = crud.create_bill(db, user.id, bill_in)
    return bill

@app.get("/bills", response_model=list[schemas.BillOut])
def list_bills(db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bills = crud.get_bills_for_user(db, user.id)
    return bills

@app.get("/bills/{bill_id}", response_model=schemas.BillOut)
def get_bill(bill_id: int, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bill = crud.get_bill(db, bill_id)
    if not bill or bill.user_id != user.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@app.put("/bills/{bill_id}", response_model=schemas.BillOut)
def update_bill(bill_id: int, bill_update: schemas.BillUpdate, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bill = crud.get_bill(db, bill_id)
    if not bill or bill.user_id != user.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    updated = crud.update_bill(db, bill_id, bill_update.dict(exclude_unset=True))
    return updated

from fastapi import status

@app.post("/bills/{bill_id}/mark_paid", response_model=schemas.BillOut, status_code=status.HTTP_200_OK)
def mark_paid_route(bill_id: int, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bill = crud.mark_bill_paid(db, bill_id, user.id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found or not yours")
    return bill


@app.delete("/bills/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bill = crud.get_bill(db, bill_id)
    if not bill or bill.user_id != user.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    crud.delete_bill(db, bill_id)
    return {"detail": "deleted"}


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    data = crud.get_dashboard(db, user.id)
    return data

@app.post("/payments", response_model=schemas.PaymentOut)
def create_payment_route(payload: schemas.PaymentCreate, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    p = crud.create_payment(db, user.id, payload.dict())
    return p

@app.get("/payments", response_model=list[schemas.PaymentOut])
def list_payments_route(db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    items = crud.get_payments_for_user(db, user.id)
    return items

# in backend/main.py
from backend.scheduler import start_scheduler

# after app = FastAPI(...)
start_scheduler()

from fastapi.responses import StreamingResponse
import csv
from io import StringIO
from datetime import datetime

@app.get("/payments/export")
def export_payments(month: str, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    # month format YYYY-MM
    start = datetime.fromisoformat(month + "-01")
    if start.month == 12:
        end = start.replace(year=start.year+1, month=1)
    else:
        end = start.replace(month=start.month+1)
    payments = crud.get_payments_for_user(db, user.id, 0, 1000)
    # filter by month
    rows = []
    for p in payments:
        paid_on = p.paid_on
        if not paid_on:
            continue
        if paid_on >= start and paid_on < end:
            rows.append([p.id, p.bill_id, float(p.amount), p.method, paid_on.isoformat()])
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id","bill_id","amount","method","paid_on"])
    writer.writerows(rows)
    buf.seek(0)
    filename = f"payments_{month}.csv"
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
