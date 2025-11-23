# backend/notify.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from datetime import datetime

from backend.database import SessionLocal
from backend import models

# env
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SMS_FROM = os.getenv("TWILIO_SMS_FROM")            # e.g. "+1XXXXXXXXXX" (Twilio number)
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g. "whatsapp:+14155238886" (Twilio sandbox)

def send_email(to_email: str, subject: str, content: str) -> bool:
    if not SENDGRID_API_KEY:
        print("SendGrid not configured; skipping email")
        return False
    message = Mail(from_email="no-reply@smartdues.test", to_emails=to_email, subject=subject, plain_text_content=content)
    try:
        client = SendGridAPIClient(SENDGRID_API_KEY)
        resp = client.send(message)
        print(f"[notify] Email sent {resp.status_code} to {to_email}")
        return True
    except Exception as e:
        print("[notify] SendGrid error:", e)
        return False

def send_sms(to_phone: str, body: str) -> bool:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_SMS_FROM):
        print("Twilio SMS not configured; skipping SMS")
        return False
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(body=body, from_=TWILIO_SMS_FROM, to=to_phone)
        print(f"[notify] SMS sent sid={msg.sid} to {to_phone}")
        return True
    except Exception as e:
        print("[notify] Twilio SMS error:", e)
        return False

def send_whatsapp(to_phone: str, body: str) -> bool:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM):
        print("Twilio WhatsApp not configured; skipping WhatsApp")
        return False
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(body=body, from_=TWILIO_WHATSAPP_FROM, to=f"whatsapp:{to_phone}")
        print(f"[notify] WhatsApp sent sid={msg.sid} to {to_phone}")
        return True
    except Exception as e:
        print("[notify] Twilio WhatsApp error:", e)
        return False

def log_reminder(db_session, user_id, bill_id, sent_at, channel="email"):
    # if models.ReminderLog exists, create row; otherwise print for debug
    try:
        rl = models.ReminderLog(user_id=user_id, bill_id=bill_id, reminder_sent_at=sent_at, channel=channel)
        db_session.add(rl)
        db_session.commit()
    except Exception as e:
        print("[notify] reminder log error (maybe table missing):", e)
