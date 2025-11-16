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

