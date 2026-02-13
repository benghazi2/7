import streamlit as st
import pandas as pd
import threading
import time
import json

# استيراد الموديولات المحلية
from database import save_recommendation, get_active_trades, init_db
from data_fetcher import get_live_data, get_latest_news
from technical_analysis import full_analysis
from ai_recommendation import generate_final_recommendation

st.set_page_config(page_title="Forex AI Sniper", layout="wide")

# CSS لتجميل الكروت
st.markdown("""
<style>
    .buy-card { border-left: 5px solid #00ff88; background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    .sell-card { border-left: 5px solid #ff4b4b; background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    .wait-card { border-left: 5px solid #cccccc; background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    .metric-label { font-size: 0.8em; color: #888; }
    .metric-value { font-size: 1.1em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# قائمة العملات
FOREX_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X", "BTC-USD", 
    "AUDUSD=X", "USDCAD=X", "USDCHF=X"
]

init_db()

st.title("🤖 AI Forex Sniper - لوحة التوصيات")

# تقسيم الصفحة إلى تبويبات
tab1, tab2 = st.tabs(["📊 التوصيات الحالية", "⚙️ لوحة التحكم والبحث"])

# --- التبويب 1: عرض التوصيات ---
with tab1:
    st.header("أحدث الفرص المكتشفة")
    
    if st.button("🔄 تحديث القائمة"):
        st.rerun()
        
    trades = get_active_trades()
    
    if not trades:
        st.info("لا توجد توصيات محفوظة حالياً. قم بتشغيل الفحص من التبويب الثاني.")
    else:
        # ترتيب حسب الوقت (الأحدث أولاً)
        trades.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        for trade in trades:
            # محاولة قراءة التوصية سواء كانت نص أو JSON
            try:
                rec_data = json.loads(trade.get('recommendation', '{}'))
            except:
                rec_data = {"reason": trade.get('recommendation', 'No details'), "direction": trade.get('direction', '---')}

            # تحديد اللون والنوع
            direction = str(rec_data.get('direction', trade.get('direction', ''))).upper()
            card_class = "buy-card" if "BUY" in direction or "شراء" in direction else "sell-card" if "SELL" in direction or "بيع" in direction else "wait-card"
            icon = "🟢" if "buy-card" == card_class else "🔴" if "sell-card" == card_class else "⚪"

            # عرض الكارت
            with st.container():
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h2>{icon} {trade['symbol']}</h2>
                        <span>🕒 {trade['time']}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:10px;">
                        <div><span class="metric-label">السعر</span><br><span class="metric-value">{rec_data.get('entry', '---')}</span></div>
                        <div><span class="metric-label">وقف الخسارة</span><br><span class="metric-value">{rec_data.get('sl', '---')}</span></div>
                        <div><span class="metric-label">الهدف 1</span><br><span class="metric-value">{rec_data.get('tp1', '---')}</span></div>
                        <div><span class="metric-label">القوة</span><br><span class="metric-value">{trade['score']}/100</span></div>
                    </div>
                    <p style="margin-top:10px; color:#ddd;">💡 <b>التحليل:</b> {rec_data.get('reason', '---')}</p>
                </div>
                """, unsafe_allow_html=True)

# --- التبويب 2: التحكم والتشغيل ---
with tab2:
    st.header("إعدادات الماسح الضوئي")
    
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox("الإطار الزمني (Timeframe)", ["5m", "15m", "1h", "4h"], index=1)
    
    with col2:
        st.write("حالة النظام:")
        if 'analysis_running' in st.session_state and st.session_state.analysis_running:
            st.success("الماسح يعمل في الخلفية... 🚀")
        else:
            st.warning("الماسح متوقف 🛑")

    if st.button("🚀 بدء البحث عن الفرص (Start Scanner)"):
        st.session_state.analysis_running = True
        st.rerun()

    st.markdown("---")
    st.write("📝 **سجل العمليات (Logs):**")
    st.caption("افتح الـ Terminal لترَ تفاصيل الاتصال بالذكاء الاصطناعي.")

# --- منطق البحث في الخلفية ---
def scanner_job():
    while True:
        if st.session_state.get('analysis_running', False):
            for symbol in FOREX_PAIRS:
                try:
                    df = get_live_data(symbol, timeframe)
                    if df.empty: continue
                    
                    analysis = full_analysis(df)
                    
                    # تحليل فقط إذا كانت الإشارة قوية نوعاً ما
                    if analysis['score'] >= 50:
                        news = get_latest_news(symbol.replace("=X", ""))
                        # الاتصال بالذكاء الاصطناعي
                        recommendation = generate_final_recommendation(symbol, df, analysis, news)
                        
                        # استخراج الاتجاه من الرد للحفظ
                        try:
                            rec_json = json.loads(recommendation)
                            direction = rec_json.get('direction', analysis['signal'])
                        except:
                            direction = analysis['signal']
                            
                        save_recommendation(symbol, recommendation, analysis['score'], direction)
                    
                    time.sleep(2) # تفادي الحظر
                except Exception as e:
                    print(f"Error scanning {symbol}: {e}")
            
            time.sleep(300) # انتظار 5 دقائق
        else:
            time.sleep(2)

if 'thread_started' not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=scanner_job, daemon=True)
    thread.start()