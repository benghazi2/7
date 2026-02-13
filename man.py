import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime

# استيراد الملفات المساعدة
from database import save_recommendation, get_active_trades, init_db
from data_fetcher import get_live_data, get_latest_news
from technical_analysis import full_analysis
from ai_recommendation import generate_final_recommendation
from chat_bot import trading_chat

st.set_page_config(page_title="AI Smart Trader", layout="wide")

# تهيئة الاتصال بقاعدة البيانات
init_db()

# تنسيق CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #0e1117; border-radius: 5px; }
    .buy-card { border-right: 5px solid #00ff88; background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .sell-card { border-right: 5px solid #ff4b4b; background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .wait-card { border-right: 5px solid #888; background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("💹 AI Smart Trader Pro")

# قائمة العملات للفحص
FOREX_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X", 
    "AUDUSD=X", "USDCAD=X", "USDCHF=X", "BTC-USD"
]

# تقسيم الصفحة إلى 3 تبويبات
tab1, tab2, tab3 = st.tabs(["📡 التوصيات الحية", "💬 الدردشة مع AI", "⚙️ فحص السوق"])

# ==========================================
# التبويب 1: عرض التوصيات
# ==========================================
with tab1:
    st.header("آخر الفرص المكتشفة")
    
    if st.button("🔄 تحديث القائمة", key="refresh_btn"):
        st.rerun()

    trades = get_active_trades()
    
    if not trades:
        st.info("📭 لا توجد توصيات محفوظة. اذهب لتبويب 'فحص السوق' واضغط بدء الفحص.")
    else:
        # ترتيب حسب الوقت (الأحدث في الأعلى)
        trades.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        for trade in trades:
            # محاولة قراءة التوصية
            try:
                rec_data = json.loads(trade.get('recommendation', '{}'))
            except:
                # إذا كانت التوصية نصاً عادياً وليست JSON
                rec_data = {"reason": trade.get('recommendation', '...'), "direction": trade.get('direction', 'WAIT')}

            # تحديد الألوان والاتجاه
            raw_dir = str(rec_data.get('direction', trade.get('direction', ''))).upper()
            
            if "BUY" in raw_dir or "شراء" in raw_dir:
                card_class = "buy-card"
                icon = "🟢 شراء"
                color = "#00ff88"
            elif "SELL" in raw_dir or "بيع" in raw_dir:
                card_class = "sell-card"
                icon = "🔴 بيع"
                color = "#ff4b4b"
            else:
                card_class = "wait-card"
                icon = "⚪ انتظار/محايد"
                color = "#cccccc"

            # عرض الكارت
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <h3 style="margin:0; color:{color};">{trade['symbol']} {icon}</h3>
                    <small style="color:#888;">{trade['time']}</small>
                </div>
                <div style="display:flex; justify-content:space-between; background:#1e1e1e; padding:10px; border-radius:5px;">
                    <div style="text-align:center;"><b>دخول</b><br>{rec_data.get('entry', '---')}</div>
                    <div style="text-align:center;"><b>هدف 1</b><br>{rec_data.get('tp1', '---')}</div>
                    <div style="text-align:center;"><b>وقف خسارة</b><br>{rec_data.get('sl', '---')}</div>
                    <div style="text-align:center;"><b>القوة</b><br>{trade.get('score', 0)}%</div>
                </div>
                <p style="margin-top:10px; font-size:0.9em;">💡 <b>التحليل:</b> {rec_data.get('reason', '...')}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# التبويب 2: الدردشة مع الذكاء الاصطناعي
# ==========================================
with tab2:
    st.header("💬 المحلل المالي الذكي")
    st.caption("اسألني عن أي زوج، استراتيجية، أو تحليل السوق الحالي.")
    
    # قائمة منسدلة لاختيار الزوج للحديث عنه
    selected_pair = st.selectbox("اختر زوجاً للحديث عنه:", FOREX_PAIRS)
    
    # استدعاء دالة الشات
    trading_chat(selected_pair)

# ==========================================
# التبويب 3: فحص السوق (Scanner)
# ==========================================
with tab3:
    st.header("🔍 الماسح الضوئي للسوق")
    
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox("الإطار الزمني", ["5m", "15m", "1h", "4h"], index=1)
    
    st.write("---")
    
    # زر الفحص الفوري (بدون خلفية لتضمن عمله)
    if st.button("🚀 ابدأ فحص جميع العملات الآن", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(FOREX_PAIRS):
            status_text.text(f"جاري تحليل {symbol}...")
            
            try:
                # 1. جلب البيانات
                df = get_live_data(symbol, timeframe)
                if df.empty:
                    st.warning(f"⚠️ لا توجد بيانات لـ {symbol}")
                    continue

                # 2. التحليل الفني
                analysis = full_analysis(df)
                
                # 3. جلب الأخبار والاتصال بالذكاء الاصطناعي
                # ملاحظة: ألغيت شرط السكور > 50 لتظهر النتائج دائماً للتجربة
                news = get_latest_news(symbol.replace("=X", ""))
                recommendation = generate_final_recommendation(symbol, df, analysis, news)
                
                # 4. محاولة استخراج الاتجاه للحفظ الصحيح
                try:
                    rec_json = json.loads(recommendation)
                    direction = rec_json.get('direction', analysis['signal'])
                except:
                    direction = analysis['signal']

                # 5. الحفظ
                save_recommendation(symbol, recommendation, analysis['score'], direction)
                
            except Exception as e:
                st.error(f"خطأ في {symbol}: {e}")
            
            # تحديث الشريط
            progress_bar.progress((i + 1) / len(FOREX_PAIRS))
        
        status_text.success("✅ اكتمل الفحص! انتقل لتبويب 'التوصيات الحية' لرؤية النتائج.")
        time.sleep(1)
        st.rerun()