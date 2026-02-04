import streamlit as st
import requests

# إعداد الصفحة
st.set_page_config(page_title="Chat with Kimi", page_icon="🤖")

st.title("🤖 محادثة مع الذكاء الاصطناعي")

# 1. إعداد الرابط والمفتاح السري
# ملاحظة: الموديل Kimi-K2.5 ضخم، إذا لم يعمل على الـ API المجاني
# يمكنك استبدال الرابط أدناه بموديل أخف مثل: "meta-llama/Llama-3.2-11B-Vision-Instruct"
API_URL = "https://api-inference.huggingface.co/models/moonshotai/Kimi-K2.5"

# سنقوم بجلب المفتاح السري من إعدادات السيرفر لاحقاً لحمايته
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# 2. واجهة المستخدم
user_input = st.text_input("اكتب رسالتك هنا:", "")

if st.button("إرسال"):
    if not user_input:
        st.warning("الرجاء كتابة رسالة أولاً")
    else:
        with st.spinner('جاري الاتصال بـ Hugging Face...'):
            try:
                # تجهيز الرسالة كما يطلبها الموديل (صورة + نص)
                # بما أنك طلبت نفس كودك السابق، سنرسل نفس الصورة الثابتة
                payload = {
                    "inputs": user_input, 
                    "parameters": {"max_new_tokens": 100} 
                    # ملاحظة: بعض الموديلات تتطلب هيكلة مختلفة للـ JSON
                    # إذا فشل هذا الموديل، فالسبب غالباً أنه لا يدعم الـ API المجاني المباشر
                }
                
                output = query(payload)
                
                # عرض النتيجة
                if isinstance(output, list) and 'generated_text' in output[0]:
                    st.success(output[0]['generated_text'])
                elif isinstance(output, dict) and 'error' in output:
                    st.error(f"خطأ من Hugging Face: {output['error']}")
                else:
                    st.write(output) # عرض الرد الخام في حال كان التنسيق مختلفاً
                    
            except Exception as e:
                st.error(f"حدث خطأ: {e}")