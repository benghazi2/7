# technical_analysis.py -    + SMC
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime

def full_analysis(df):
    if len(df) < 50:
        return {"error": "  ", "score": 0}
    
    df = df.copy()
    result = {"indicators": {}, "smc": {}, "score": 0, "signal": ""}
    
    #  
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['MACD'] = ta.macd(df['Close'])
    df['BB'] = ta.bbands(df['Close'], length=20)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    #  RSI
    rsi = latest['RSI']
    if rsi < 30:
        result['indicators']['rsi_signal'] = " "
        result['score'] += 20
    elif rsi > 70:
        result['indicators']['rsi_signal'] = " "
        result['score'] += 15
    
    #  MACD
    if not pd.isna(latest['MACD_12_26_9']):
        if latest['MACD_12_26_9'] > latest['MACDs_12_26_9'] and prev['MACD_12_26_9'] <= prev['MACDs_12_26_9']:
            result['indicators']['macd_signal'] = " "
            result['score'] += 25
        elif latest['MACD_12_26_9'] < latest['MACDs_12_26_9'] and prev['MACD_12_26_9'] >= prev['MACDs_12_26_9']:
            result['indicators']['macd_signal'] = " "
            result['score'] += 20
    
    #  Order Block ()
    high_vol = df['Volume'].rolling(20).mean().iloc[-1]
    if latest['Volume'] > high_vol * 1.5:
        if latest['Close'] > latest['Open']:
            result['smc']['order_block'] = " "
            result['score'] += 30
        else:
            result['smc']['order_block'] = " "
            result['score'] += 25
    
    #  Fair Value Gap (FVG)
    if len(df) > 3:
        prev2 = df.iloc[-3]
        prev1 = df.iloc[-2]
        if prev2['Low'] > prev1['High']:
            result['smc']['fvg'] = f"    {prev1['High']}"
            result['score'] += 35
        elif prev2['High'] < prev1['Low']:
            result['smc']['fvg'] = f"    {prev1['Low']}"
            result['score'] += 30
    
    #   
    if result['score'] >= 80:
        result['signal'] = " "
    elif result['score'] >= 60:
        result['signal'] = ""
    elif result['score'] <= 30:
        result['signal'] = " "
    elif result['score'] <= 45:
        result['signal'] = ""
    else:
        result['signal'] = ""
    
    result['final_score'] = min(100, result['score'])
    
    return result