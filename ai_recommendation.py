# ai_recommendation.py - إصلاح الاتصال + موديل مستقر
import requests
import json
from config import GROK_API_KEY

def generate_final_recommendation(symbol, df, analysis, news_summary=""):
    try:
        latest = df.iloc[-1]
        price = round(latest['Close'], 5)
        
        # تحضير الرسالة
        prompt = f"""
        Role: Expert Forex Analyst (SMC Strategy).
        Symbol: {symbol}
        Price: {price}
        Technical Score: {analysis['final_score']}/100
        Signal: {analysis['signal']}
        RSI: {latest['RSI']:.1f}
        News: {news_summary[:150]}
        
        Task: Provide a strict trading signal in Arabic (JSON format).
        Format:
        {{
            "direction": "BUY/SELL/WAIT",
            "entry": "price",
            "sl": "price",
            "tp1": "price",
            "tp2": "price",
            "reason": "short text"
        }}
        """

        # إعدادات الاتصال بـ Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # استخدام موديل خفيف وسريع جداً ومستقر
        data = {
            "model": "llama3-8b-8192", 
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300,
            "response_format": {"type": "json_object"} # إجبار الرد أن يكون JSON منظم
        }
        
        print(f"⏳ جاري الاتصال بالذكاء الاصطناعي لتحليل {symbol}...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print(f"✅ تم استلام التحليل بنجاح لـ {symbol}")
            return content
        else:
            # طباعة الخطأ الحقيقي في الكونسول
            print(f"❌ AI Error ({symbol}): {response.status_code} - {response.text}")
            return generate_fallback_recommendation(symbol, price, analysis, news_summary)
            
    except Exception as e:
        print(f"❌ Connection Exception: {e}")
        return generate_fallback_recommendation(symbol, price, analysis, news_summary)

def generate_fallback_recommendation(symbol, price, analysis, news):
    # دالة الطوارئ عند فشل الاتصال
    signal = analysis['signal']
    
    if "شراء" in str(signal) or "Buy" in str(signal):
        direction = "BUY 🟢"
        sl = price * 0.995
        tp1 = price * 1.01
        tp2 = price * 1.02
    elif "بيع" in str(signal) or "Sell" in str(signal):
        direction = "SELL 🔴"
        sl = price * 1.005
        tp1 = price * 0.99
        tp2 = price * 0.98
    else:
        direction = "WAIT ⚪"
        sl = tp1 = tp2 = price

    # إرجاع نص يشبه JSON ليعمل مع الكود الجديد
    return json.dumps({
        "direction": direction,
        "entry": str(price),
        "sl": str(round(sl, 5)),
        "tp1": str(round(tp1, 5)),
        "tp2": str(round(tp2, 5)),
        "reason": f"تحليل فني بحت (بدون AI): المؤشرات تشير إلى {signal} بقوة {analysis['final_score']}%"
    }, ensure_ascii=False)