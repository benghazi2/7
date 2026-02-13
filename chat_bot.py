# chat_bot.py - محدث ليعمل مع Groq
import streamlit as st
import requests
from config import GROK_API_KEY

def trading_chat(symbol):
    # تهيئة سجل الرسائل
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل القديمة
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # استقبال السؤال
    if prompt := st.chat_input(f"اسألني عن {symbol}..."):
        # إضافة رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # الرد من Groq AI
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = get_groq_chat_response(prompt, symbol)
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def get_groq_chat_response(query, symbol):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""
        أنت مساعد تداول محترف وخبير في أسواق المال.
        السياق الحالي: المستخدم يسأل عن الزوج {symbol}.
        أجب باللغة العربية بأسلوب مختصر، دقيق، ومبني على التحليل الفني.
        """
        
        data = {
            "model": "llama3-8b-8192",  # موديل سريع جداً
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"عذراً، حدث خطأ في الخادم ({response.status_code})."
    except Exception as e:
        return f"خطأ في الاتصال: {e}"