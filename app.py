import streamlit as st
import requests

# إعداد الصفحة
st.set_page_config(page_title="Chat AI", page_icon="🤖", layout="centered")

st.title("🤖 محادثة مع الذكاء الاصطناعي")

# ------------------------------------------------------------------
# إعدادات الاتصال بالموديل
# ------------------------------------------------------------------

# تم تحديث الرابط من api-inference إلى router كما طلب Hugging Face
# الموديل الحالي: Kimi-K2.5
API_URL = "https://router.huggingface.co/models/moonshotai/Kimi-K2.5"

# --- خيار بديل (احتياطي) ---
# إذا لم يعمل Kimi لأنه كبير جداً، قم بحذف علامة # من السطر التالي وضعها أمام السطر السابق
# API_URL = "https://router.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"

# التحقق من وجود المفتاح السري في إعدادات Streamlit
if 'HF_TOKEN' in st.secrets:
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
else:
    st.error("⚠️ لم يتم العثور على HF_TOKEN في إعدادات Secrets.")
    st.stop()

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

# ------------------------------------------------------------------
# واجهة المستخدم
# ------------------------------------------------------------------

# حقل إدخال النص
user_input = st.text_area("اكتب رسالتك هنا:", height=100)

# زر الإرسال
if st.button("إرسال", type="primary"):
    if not user_input.strip():
        st.warning("الرجاء كتابة نص قبل الإرسال.")
    else:
        with st.spinner('جاري التفكير... (قد يستغرق وقتاً للموديلات الكبيرة)'):
            # إعداد البيانات للإرسال
            # نرسل النص فقط، الموديل سيفهمه كسؤال
            payload = {
                "inputs": user_input,
                "parameters": {
                    "max_new_tokens": 250,  # عدد الكلمات في الرد
                    "return_full_text": False 
                }
            }

            output = query(payload)

            # -------------------------------------------------------
            # معالجة وعرض النتيجة
            # -------------------------------------------------------
            if isinstance(output, list) and len(output) > 0 and 'generated_text' in output[0]:
                st.success("الرد:")
                st.write(output[0]['generated_text'])
            
            elif isinstance(output, dict) and 'error' in output:
                st.error(f"حدث خطأ من المصدر: {output['error']}")
                # نصيحة للمستخدم إذا كان الخطأ بسبب حجم الموديل
                if "loading" in output['error'].lower():
                    st.info("💡 الموديل قيد التحميل، حاول الضغط على إرسال مرة أخرى بعد 30 ثانية.")
                if "too large" in output['error'].lower():
                    st.warning("💡 الموديل المختار كبير جداً على الخطة المجانية. جرب تغيير الرابط في الكود لاستخدام Llama.")
            else:
                st.write("رد غير متوقع:", output)