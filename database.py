# database.py - نسخة آمنة لـ Streamlit Cloud
import firebase_admin
from firebase_admin import credentials, db
import json
import os

# جلب الـ credentials من Streamlit Secrets
if "FIREBASE_CREDENTIALS" in os.environ:
    firebase_credentials = json.loads(os.environ["FIREBASE_CREDENTIALS"])
else:
    import streamlit as st
    firebase_credentials = st.secrets["FIREBASE_CREDENTIALS"]

# تهيئة Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://my-goodbarber-projet-261703-default-rtdb.firebaseio.com/'
    })

ref = db.reference('/')

# باقي الدوال زي ما هي
def init_db():
    pass

def save_recommendation(symbol, recommendation, score):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "symbol": symbol,
        "recommendation": recommendation,
        "score": score,
        "time": timestamp,
        "progress": 0,
        "pnl": 0,
        "status": "open"
    }
    try:
        ref.child("recommendations").push(data)
        ref.child("active_trades").child(symbol.replace("=X", "")).set(data)
    except:
        pass

def get_active_trades():
    try:
        data = ref.child("active_trades").get()
        return list(data.values()) if data else []
    except:
        return []