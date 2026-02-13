# database.py - الاتصال بـ Firebase وحفظ البيانات
import firebase_admin
from firebase_admin import credentials, db
from config import FIREBASE_CONFIG
import json
import os
from datetime import datetime

# منع التكرار في التهيئة
if not firebase_admin._apps:
    # استخدام الملف المحلي إذا وجد
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        cred = credentials.Certificate(FIREBASE_CONFIG)
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://my-goodbarber-projet-261703-default-rtdb.firebaseio.com/'
    })

# مرجع قاعدة البيانات
ref = db.reference('/')

def init_db():
    """تهيئة الهيكل الأساسي"""
    try:
        ref.child("recommendations").set({})
        ref.child("active_trades").set({})
        print("تم تهيئة قاعدة البيانات")
    except:
        pass

def save_recommendation(symbol, recommendation, score):
    """حفظ توصية جديدة"""
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
    ref.child("recommendations").push(data)
    ref.child("active_trades").child(symbol.replace("=X", "")).set(data)

def get_active_trades():
    """جلب الصفقات النشطة"""
    try:
        data = ref.child("active_trades").get()
        if data:
            return list(data.values())
        else:
            return []
    except:
        return []

def update_trade_pnl(symbol, pnl, progress=0):
    """تحديث الربح والخسارة"""
    clean_symbol = symbol.replace("=X", "")
    ref.child("active_trades").child(clean_symbol).update({
        "pnl": round(pnl, 2),
        "progress": progress,
        "last_update": datetime.now().strftime("%H:%M")
    })

print("تم تحميل وحدة قاعدة البيانات بنجاح")