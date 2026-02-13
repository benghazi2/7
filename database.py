# database.py - تم التعديل لحفظ اتجاه الصفقة
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json
from datetime import datetime

ref = None

def init_db():
    global ref
    if firebase_admin._apps:
        try:
            ref = db.reference('/')
        except:
            pass
        return

    try:
        raw_creds = st.secrets["FIREBASE_CREDENTIALS"]
        if isinstance(raw_creds, str):
            firebase_creds = json.loads(raw_creds)
        else:
            firebase_creds = dict(raw_creds)

        if "private_key" in firebase_creds:
            firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")

        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://my-goodbarber-projet-261703-default-rtdb.firebaseio.com/'
        })
        ref = db.reference('/')
    except Exception as e:
        print(f"Firebase Connection Error: {e}")
        ref = None

init_db()

# --- التعديل هنا: إضافة parameter جديد يسمى direction ---
def save_recommendation(symbol, recommendation, score, direction):
    if ref is None: return
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "symbol": symbol,
            "recommendation": recommendation,
            "score": score,
            "direction": direction,  # تم إضافة هذا الحقل
            "time": timestamp,
            "progress": 0,
            "pnl": 0,
            "status": "open"
        }
        ref.child("recommendations").push(data)
        clean_symbol = symbol.replace("=X", "").replace(".", "_")
        ref.child("active_trades").child(clean_symbol).set(data)
    except Exception as e:
        print(f"Error saving: {e}")

def get_active_trades():
    if ref is None: return []
    try:
        data = ref.child("active_trades").get()
        if not data: return []
        # التأكد من أن البيانات قائمة
        return list(data.values())
    except:
        return []