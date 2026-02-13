# ai_recommendation.py - تم الإصلاح ليعمل مع Groq
import requests
import json
from config import GROK_API_KEY
from datetime import datetime

def generate_final_recommendation(symbol, df, analysis, news_summary=""):
    try:
        latest = df.iloc[-1]
        price = round(latest['Close'], 5)
        # حساب التغير
        prev_close = df['Close'].iloc[-2]
        change = round(((latest['Close'] - prev_close) / prev_close) * 100, 2)
        
        # تجهيز البرومبت
        prompt = f"""
        أنت خبير تداول محترف (SMC & ICT).
        الزوج: {symbol}
        السعر الحالي: {price}
        التغير: {change}%
        التحليل الفني: {analysis['final_score']}/100
        الإشارة الفنية: {analysis['signal']}
        RSI: {latest['RSI']:.1f}
        Order Block: {analysis['smc'].get('order_block', 'لا يوجد')}
        FVG: {analysis['smc'].get('fvg', 'لا يوجد')}
        الأخبار: {news_summary[:200] if news_summary else 'لا توجد أخبار مؤثرة'}

        المطلوب: تحليل دقيق ومختصر جداً (باللغة العربية) يتضمن:
        1. الاتجاه المتوقع (صعود/هبوط).
        2. مناطق الدخول (Entry).
        3. وقف الخسارة (SL).
        4. الأهداف (TP1, TP2).
        5. السبب الفني باختصار.
        """

        # --- التصحيح: استخدام Groq API بدلاً من xAI لأن المفتاح gsk_ ---
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # استخدام موديل Llama 3 القوي والسريع
        data = {
            "model": "llama-3.3-70b-versatile", 
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 400
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"AI Error {response.status_code}: {response.text}")
            return generate_fallback_recommendation(symbol, price, analysis, news_summary)
            
    except Exception as e:
        print(f"AI Connection Exception: {e}")
        return generate_fallback_recommendation(symbol, price, analysis, news_summary)

def generate_fallback_recommendation(symbol, price, analysis, news):
    # دالة احتياطية في حال انقطاع النت أو فشل الذكاء الاصطناعي
    signal = analysis['signal']
    score = analysis['final_score']
    
    direction = "شراء 🟢" if "شراء" in signal else "بيع 🔴" if "بيع" in signal else "محايد ⚪"
    
    if "شراء" in signal:
        sl = price * 0.995
        tp = price * 1.01
    else:
        sl = price * 1.005
        tp = price * 0.99

    return f"""
    ⚠️ *تحليل احتياطي (فشل الاتصال بالذكاء الاصطناعي)*
    
    الزوج: {symbol}
    الاتجاه: {direction}
    القوة: {score}/100
    
    نطاق الدخول: {price}
    هدف تقريبي: {tp:.5f}
    وقف خسارة: {sl:.5f}
    
    سبب الإشارة: المؤشرات الفنية تشير إلى {signal}.
    """