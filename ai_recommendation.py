# ai_recommendation.py -     Grok-4
import requests
from config import GROK_API_KEY
from datetime import datetime

def generate_final_recommendation(symbol, df, analysis, news_summary=""):
    latest = df.iloc[-1]
    price = round(latest['Close'], 5)
    change = round(((latest['Close'] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100, 2)
    
    prompt = f"""
       .
       : {symbol}

 :
-  : {price}
- : {change}%
-  : {analysis['final_score']}/100
-  : {analysis['signal']}
- RSI: {latest['RSI']:.1f}
- Order Block: {analysis['smc'].get('order_block', ' ')}
- FVG: {analysis['smc'].get('fvg', ' ')}
-  : {news_summary[:200] if news_summary else '   '}

   (150-250 )  :
1.   ( /  / )
2.   
3.  
4.   
5.    
6.   ( +  +  )

      Goldman Sachs  JPMorgan.
  "  " .
"""

    try:
        url = "https://api.grok.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 600
        }
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            recommendation = response.json()['choices'][0]['message']['content']
            return recommendation
        else:
            return generate_fallback_recommendation(symbol, price, analysis, news_summary)
    except:
        return generate_fallback_recommendation(symbol, price, analysis, news_summary)

def generate_fallback_recommendation(symbol, price, analysis, news):
    signal = analysis['signal']
    score = analysis['final_score']
    if "" in signal:
        direction = ""
        entry = price
        sl = round(price * 0.995, 5)
        tp1 = round(price * 1.015, 5)
        tp2 = round(price * 1.03, 5)
    elif "" in signal:
        direction = ""
        entry = price
        sl = round(price * 1.005, 5)
        tp1 = round(price * 0.985, 5)
        tp2 = round(price * 0.97, 5)
    else:
        direction = ""
        return f"   {symbol}: {direction}\n : {score}/100\n     ."

    return f"""
   - {symbol}

: {direction} ({signal})
 : {price}
 : {entry}
 : {sl}
 : {tp1}
 : {tp2}
 /: 1:3

:
   {signal}  {score}/100    SMC  .
  {analysis['smc'].get('order_block', ' / ')}.
 : {news[:100] if news else ''}.

 :    .
"""