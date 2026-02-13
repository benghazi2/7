import streamlit as st
import pandas as pd
import threading
import time

# استيراد الموديولات المحلية
from database import save_recommendation, get_active_trades, init_db
from data_fetcher import get_live_data, get_latest_news
from technical_analysis import full_analysis
from ai_recommendation import generate_final_recommendation
from chat_bot import trading_chat

st.set_page_config(page_title="AI Smart Trader Pro", layout="wide", initial_sidebar_state="expanded")

# قائمة العملات التي سيتم فحصها
FOREX_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X", "EURAUD=X", "XAUUSD=X"
]

# تهيئة قاعدة البيانات
init_db()

st.title("AI Smart Trader Pro - الماسح الضوئي الشامل 🚀")

# الشريط الجانبي
with st.sidebar:
    st.header("لوحة التحكم")
    st.write(f"عدد الأزواج المتاحة للفحص: {len(FOREX_PAIRS)}")
    timeframe = st.selectbox("الإطار الزمني", ["5m", "15m", "1h", "4h"], index=1)
    
    # زر التشغيل
    if st.button("بدء الفحص الشامل (All Pairs)"):
        if 'analysis_running' not in st.session_state:
            st.session_state.analysis_running = True
            st.success("تم تشغيل الماسح الضوئي في الخلفية!")
        else:
            st.warning("الماسح يعمل بالفعل.")

    st.markdown("---")
    selected_symbol_chat = st.selectbox("اختر زوجاً للدردشة", FOREX_PAIRS)

# وظيفة التحليل التلقائي (Scanner Logic)
def auto_analysis_loop():
    while True:
        if st.session_state.get('analysis_running', False):
            print("--- بدء دورة فحص جديدة ---")
            
            for symbol in FOREX_PAIRS:
                try:
                    # 1. جلب البيانات
                    df = get_live_data(symbol, timeframe)
                    if df.empty: continue

                    # 2. التحليل الفني
                    analysis = full_analysis(df)
                    
                    # نفلتر: فقط الصفقات القوية (أكثر من 55%) يتم إرسالها للذكاء الاصطناعي لتوفير الوقت
                    if analysis['score'] >= 55:
                        news = get_latest_news(symbol.replace("=X", ""))
                        
                        # 3. تحليل الذكاء الاصطناعي
                        recommendation = generate_final_recommendation(symbol, df, analysis, news)
                        
                        # 4. الحفظ في قاعدة البيانات
                        save_recommendation(symbol, recommendation, analysis['score'], analysis['signal'])
                        print(f"✅ تم تحليل {symbol}: {analysis['signal']} ({analysis['score']})")
                    else:
                        print(f"⏭️ تخطي {symbol} - إشارة ضعيفة ({analysis['score']})")
                        
                    # انتظار بسيط لتجنب الحظر من Yahoo Finance
                    time.sleep(2) 
                    
                except Exception as e:
                    print(f"Error scanning {symbol}: {e}")
            
            print("--- انتهت الدورة، استراحة 5 دقائق ---")
            time.sleep(300) # استراحة 5 دقائق بعد فحص كل الأزواج
        else:
            time.sleep(5) # التحقق كل 5 ثواني إذا تم تفعيل الزر

# تشغيل الخيط (Thread) في الخلفية مرة واحدة
if 'thread_started' not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=auto_analysis_loop, daemon=True)
    thread.start()

# --- واجهة العرض ---

# 1. عرض الصفقات النشطة
st.subheader("📡 الرادار الحي - أحدث الفرص المكتشفة")
trades = get_active_trades()

# عرض الصفقات في كروت
if trades:
    # ترتيب الصفقات حسب الأحدث
    trades.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    for trade in trades[:10]: # عرض آخر 10 فقط
        with st.container():
            # تنسيق الألوان حسب الاتجاه
            direction = trade.get('direction', '---')
            color = "#00ff88" if "شراء" in direction or "Buy" in direction else "#ff4b4b" if "بيع" in direction or "Sell" in direction else "#ffffff"
            
            st.markdown(f"""
            <div style="border:1px solid {color}; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:{color}; margin:0;">{trade.get('symbol')} - {direction}</h3>
                <p>🕒 {trade.get('time')} | 💪 القوة: {trade.get('score')}/100</p>
                <details>
                    <summary>عرض تحليل الذكاء الاصطناعي</summary>
                    <p>{trade.get('recommendation')}</p>
                </details>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("جاري الفحص... اضغط 'بدء الفحص الشامل' وانتظر النتائج.")

# 2. الدردشة
st.markdown("---")
st.subheader(f"💬 المحلل الذكي - {selected_symbol_chat}")
trading_chat(selected_symbol_chat)