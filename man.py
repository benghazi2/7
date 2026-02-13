import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
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
        st.success("تم تفعيل التحليل التلقائي")

# وظيفة التحليل التلقائي
def auto_analysis():
    while True:
        try:
            df = get_live_data(symbol, timeframe)
            news = get_latest_news(symbol.replace("=X", ""))
            analysis = full_analysis(df)
            recommendation = generate_final_recommendation(symbol, df, analysis, news)
            save_recommendation(symbol, recommendation, analysis['score'])
            st.rerun()
        except:
            pass
        time.sleep(300)  # كل 5 دقائق

# تشغيل التحليل التلقائي في الخلفية
if 'auto_started' not in st.session_state:
    thread = threading.Thread(target=auto_analysis, daemon=True)
    thread.start()
    st.session_state.auto_started = True

# عرض التوصيات الحية
st.subheader("التوصيات الحية")
trades = get_active_trades()
for trade in trades[-10:]:
    col1, col2, col3, col4, col5 = st.columns([3,1,1,1,2])
    col1.markdown(f"**{trade['symbol']}** • {trade['direction']} • {trade['time']}")
    col2.progress(trade['progress']/100)
    col3.markdown(f"**{trade['progress']}٪**")
    pnl = trade['pnl']
    col4.markdown(f"**{pnl:+.1f}** pips" if pnl != 0 else "-")
    col5.markdown(f"قوة: {trade['score']}/100")

# الدردشة مع الذكاء الاصطناعي
st.subheader("الدردشة مع المحلل الذكي")
trading_chat(symbol)

st.caption("AI Smart Trader Pro © 2025 - مدعوم بـ Grok 4")