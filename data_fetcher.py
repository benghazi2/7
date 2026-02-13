# data_fetcher.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_live_data(symbol, interval="15m"):
    """
    جلب بيانات الأسعار الحية من Yahoo Finance
    """
    try:
        # تحديد المدة الزمنية المناسبة بناءً على الفريم (لضمان وجود داتا كافية للمؤشرات)
        period_map = {
            "1m": "2d",    # دقيقتين يحتاج يومين
            "5m": "5d",    # 5 دقائق يحتاج 5 أيام
            "15m": "1mo",  # ربع ساعة يحتاج شهر
            "30m": "1mo",
            "1h": "1mo",
            "4h": "3mo",   # 4 ساعات يحتاج 3 شهور
            "1d": "1y",    # اليومي يحتاج سنة
            "1wk": "2y"
        }
        
        # اختيار المدة أو استخدام الافتراضي (شهر واحد)
        period = period_map.get(interval, "1mo")
        
        # تحميل البيانات
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        
        # التحقق من أن البيانات غير فارغة
        if df.empty:
            print(f"Warning: No data found for {symbol}")
            return pd.DataFrame()
            
        # معالجة البيانات (تسطيح الترويسة في حال كانت MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # التأكد من وجود الأعمدة الأساسية
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def get_latest_news(symbol):
    """
    جلب آخر الأخبار المتعلقة بالعملة أو السهم
    """
    try:
        # بعض الأزواج تحتاج إضافة =X للبحث في الأخبار إذا لم تكن موجودة
        search_symbol = symbol
        if "USD" in symbol and "=X" not in symbol and len(symbol) == 6:
             search_symbol = f"{symbol}=X"

        ticker = yf.Ticker(search_symbol)
        news_list = ticker.news
        
        summary = ""
        if news_list:
            # نأخذ أحدث 3 أخبار فقط
            for item in news_list[:3]:
                title = item.get('title', '')
                publisher = item.get('publisher', '')
                summary += f"- {title} ({publisher})\n"
        
        if not summary:
            return "لا توجد أخبار حديثة هامة متاحة حالياً."
            
        return summary

    except Exception as e:
        # في حالة حدوث خطأ، نعيد رسالة فارغة أو تنبيه بسيط
        return "تعذر جلب الأخبار في الوقت الحالي."