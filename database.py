# database.py - تم إصلاح الاتصال بـ Firebase
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
from datetime import datetime

# --- بداية التعديل والإصلاح ---
# التحقق من أن Firebase لم يتم تشغيله مسبقاً لتجنب الأخطاء عند تحديث الصفحة
if not firebase_admin._apps:
    try:
        # جلب البيانات من Streamlit Secrets وتحويلها إلى قاموس (Dictionary)
        # ملاحظة: يجب أن يكون لديك قسم [FIREBASE_CREDENTIALS] في إعدادات الـ Secrets
        firebase_creds = dict(st.secrets["FIREBASE_CREDENTIALS"])
        
        # هذا السطر هو أهم إصلاح: يقوم بتصحيح تنسيق المفتاح الخاص
        if "private_key" in firebase_creds:
            firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")

        # إنشاء الاتصال
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://my-goodbarber-projet-261703-default-rtdb.firebaseio.com/'
        })
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال بقاعدة البيانات: {e}")

# تحديد مرجع قاعدة البيانات
try:
    ref = db.reference('/')
except:
    ref = None
# --- نهاية التعديل والإصلاح ---

# دالة تهيئة وهمية (لأننا قمنا بالتهيئة بالأعلى بالفعل)
def init_db():
    pass

# دالة حفظ التوصيات (كما هي في ملفك الأصلي)
def save_recommendation(symbol, recommendation, score):
    if ref is None: return # حماية في حال فشل الاتصال
    
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
        # تنظيف الرمز من =X لتسهيل القراءة
        clean_symbol = symbol.replace("=X", "")
        ref.child("active_trades").child(clean_symbol).set(data)
    except Exception as e:
        print(f"Error saving data: {e}")

# دالة جلب الصفقات النشطة (كما هي في ملفك الأصلي)
def get_active_trades():
    if ref is None: return [] # حماية في حال فشل الاتصال
    
    try:
        data = ref.child("active_trades").get()
        return list(data.values()) if data else []
    except:
        return []