# backend/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta, datetime
from backend.database import SessionLocal
from backend import models
import os
from dotenv import load_dotenv
from backend.notify import send_email, send_sms, send_whatsapp, log_reminder

load_dotenv()

sched = BackgroundScheduler()

def check_and_send_reminders():
    db = SessionLocal()
    try:
        today = date.today()
        # fetch unpaid bills with reminder_days not null
        bills = db.query(models.Bill).filter(models.Bill.is_paid == False).all()
        for b in bills:
            if not b.reminder_days:
                continue
            # parse "7,3,1"
            try:
                days_list = [int(x.strip()) for x in str(b.reminder_days).split(",") if x.strip().isdigit()]
            except Exception:
                days_list = []
            for days in days_list:
                remind_date = b.due_date - timedelta(days=days)
                if remind_date == today:
                    user = db.query(models.User).filter(models.User.id == b.user_id).first()
                    if not user:
                        continue
                    subject = f"Reminder: {b.title} due in {days} day(s)"
                    body = f"Your bill '{b.title}' of amount ₹{b.amount} is due on {b.due_date}. This is a {days}-day reminder."
                    # send email
                    if user.email:
                        send_email(user.email, subject, body)
                        log_reminder(db, user.id, b.id, datetime.utcnow(), channel="email")
                    # send SMS
                    if user.phone:
                        send_sms(user.phone, body)
                        log_reminder(db, user.id, b.id, datetime.utcnow(), channel="sms")
                    # send WhatsApp
                    if user.phone:
                        send_whatsapp(user.phone, body)
                        log_reminder(db, user.id, b.id, datetime.utcnow(), channel="whatsapp")
    finally:
        db.close()

def start_scheduler():
    # For dev: run every 1 minute (fast feedback). For production, use interval=minutes=60 or cron.
    sched.add_job(check_and_send_reminders, "interval", minutes=1, id="reminder_job", replace_existing=True)
    sched.start()
