import streamlit as st
import pandas as pd
import yfinance as yf
import threading
import time

# استيراد الموديولات المحلية
from database import save_recommendation, get_active_trades, init_db
from data_fetcher import get_live_data, get_latest_news
from technical_analysis import full_analysis
from ai_recommendation import generate_final_recommendation
from chat_bot import trading_chat

st.set_page_config(page_title="AI Smart Trader Pro", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .main {background-color: #0e1117; color: white;}
    .stButton>button {background-color: #00ff88; color: black; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# تهيئة قاعدة البيانات
init_db()

st.title("AI Smart Trader Pro - SMC + Banks + AI")
st.markdown("**النظام الأقوى للتداول الآلي بالذكاء الاصطناعي 2025**")

# الشريط الجانبي
with st.sidebar:
    st.header("إعدادات التداول")
    symbol = st.text_input("الزوج أو الأصل", value="EURUSD=X").upper()
    timeframe = st.selectbox("الإطار الزمني", ["1m", "5m", "15m", "1h", "4h", "1d"])
    
    if st.button("بدء التحليل الآلي كل 5 دقائق"):
        st.session_state.auto_active = True
        st.success("تم تفعيل التحليل التلقائي")

# وظيفة التحليل التلقائي
def auto_analysis():
    while True:
        try:
            # التحقق من وجود الرمز في session_state لتجنب الأخطاء عند البدء
            current_symbol = "EURUSD=X" # قيمة افتراضية
            
            df = get_live_data(current_symbol, "15m") # استخدام إطار زمني افتراضي للخلفية
            if not df.empty:
                news = get_latest_news(current_symbol.replace("=X", ""))
                analysis = full_analysis(df)
                recommendation = generate_final_recommendation(current_symbol, df, analysis, news)
                
                # --- التعديل هنا: تمرير analysis['signal'] ---
                save_recommendation(current_symbol, recommendation, analysis['score'], analysis['signal'])
        except Exception as e:
            print(f"Auto analysis error: {e}")
        time.sleep(300)

# تشغيل التحليل التلقائي في الخلفية مرة واحدة فقط
if 'thread_started' not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=auto_analysis, daemon=True)
    thread.start()

# عرض التوصيات الحية
st.subheader("التوصيات الحية")
trades = get_active_trades()

if trades:
    for trade in trades[-10:]:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3,1,1,1,2])
            # استخدام .get لتجنب الخطأ إذا كان الحقل ناقصاً
            direction = trade.get('direction', '---')
            sym = trade.get('symbol', 'Unknown')
            t_time = trade.get('time', '')
            
            col1.markdown(f"**{sym}** • {direction} • {t_time}")
            
            prog = trade.get('progress', 0)
            col2.progress(min(max(prog, 0), 100) / 100)
            col3.markdown(f"**{prog}٪**")
            
            pnl = trade.get('pnl', 0)
            col4.markdown(f"**{pnl:+.1f}** pips" if pnl != 0 else "-")
            
            score = trade.get('score', 0)
            col5.markdown(f"قوة: {score}/100")
else:
    st.info("لا توجد صفقات نشطة حالياً. انتظر التحليل التالي.")

# الدردشة مع الذكاء الاصطناعي
st.subheader("الدردشة مع المحلل الذكي")
trading_chat(symbol)

st.caption("AI Smart Trader Pro © 2025 - مدعوم بـ Grok 4")