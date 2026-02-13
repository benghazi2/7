# chat_bot.py
import streamlit as st
import requests
from config import GROK_API_KEY

def trading_chat(symbol):
    # تهيئة سجل المحادثة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل السابقة
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # استقبال سؤال جديد
    if prompt := st.chat_input("اسألني عن السوق أو التحليل..."):
        # إضافة رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # الرد (محاكاة أو ذكاء اصطناعي)
        with st.chat_message("assistant"):
            response_text = get_grok_response(prompt, symbol)
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

def get_grok_response(query, symbol):
    # محاولة الاتصال بـ Grok API
    try:
        url = "https://api.grok.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        system_prompt = f"أنت خبير تداول مالي. العملة الحالية هي {symbol}. أجب باختصار واحترافية."
        data = {
            "model": "grok-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.5,
            "max_tokens": 300
        }
        res = requests.post(url, json=data, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return "عذراً، خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً."
    except:
        return "حدث خطأ في الاتصال بالخادم."