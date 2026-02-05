import streamlit as st
import requests
import json

# إعداد الصفحة
st.set_page_config(page_title="Chat AI", page_icon="🤖")
st.title("🤖 محادثة مع الذكاء الاصطناعي")

# ------------------------------------------------------------------
# 1. إعدادات الموديل (تم تغيير الموديل لضمان العمل)
# ------------------------------------------------------------------
# نستخدم موديل Zephyr لأنه سريع جداً ومجاني ومخصص للمحادثة
# إذا اشتغل هذا الموديل، يمكنك لاحقاً تجربة موديلات أخرى
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# جلب المفتاح السري
if 'HF_TOKEN' in st.secrets:
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
else:
    st.error("⚠️ لم يتم العثور على HF_TOKEN. تأكد من وضعه في Secrets.")
    st.stop()

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # --- كشف الأخطاء الدقيق ---
        # إذا كان الرد ليس 200 (نجاح)، نعرض الخطأ الحقيقي
        if response.status_code != 200:
            return {"error": f"Status: {response.status_code}, Msg: {response.text}"}
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

# ------------------------------------------------------------------
# 2. واجهة المستخدم
# ------------------------------------------------------------------

# إنشاء سجل للمحادثة (عشان المحادثة ما تختفي لما تضغط زر)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# حقل الإدخال الجديد (أسفل الشاشة مثل ChatGPT)
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    # 1. عرض رسالة المستخدم
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. إرسال للموديل واستقبال الرد
    with st.chat_message("assistant"):
        with st.spinner("جاري الكتابة..."):
            
            # تجهيز الطلب للموديل النصي
            payload = {
                "inputs": f"<|system|>\nYou are a helpful assistant.<|user|>\n{prompt}<|assistant|>\n",
                "parameters": {"max_new_tokens": 512}
            }
            
            output = query(payload)

            # معالجة الرد
            if isinstance(output, list) and 'generated_text' in output[0]:
                # تنظيف الرد (لإزالة نص السؤال القديم)
                full_response = output[0]['generated_text']
                # نأخذ الكلام اللي بعد كلمة assistant
                bot_reply = full_response.split("<|assistant|>\n")[-1]
                
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
            elif isinstance(output, dict) and 'error' in output:
                st.error(f"حدث خطأ: {output['error']}")
            else:
                st.warning(f"رد غير متوقع: {output}")