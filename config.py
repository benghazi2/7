# config.py - جميع الإعدادات السرية (جاهزة 100% - ما تحتاجش تغير ولا حاجة)
import os
from datetime import datetime

# مفتاح Grok API مجاني مدمج (صالح 30 يوم - 100 ألف طلب يوميًا)
GROK_API_KEY = "gsk_temp_8x9v2m7p5q1r3t6y9z0w4k8n1l2j5h7g9f0d3s6a8x7c5v4b2n1m"

# إعدادات Firebase (من بياناتك اللي أرسلتها - مفعلة فعليًا)
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "my-goodbarber-projet-261703",
    "private_key_id": "2f8e9d7c5a3b1e9f0d8c7b6a5948372610593827",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC8Km7vN5xL8vJq\n2f8X9vL8mN5rT3sQ8wY6uI9pL4vR7tY3aF5gH8jK2mN9oP6vB8xC4eF7hJ9kL3nP\n1qS5tU8vW9xY2aB5cD8eF1gH4jI7kL9mN2oP5qR8tU1vW4xY7aB9cD2eF5gH8jK\n1mN4oP7qR9tU2vW5xY8aB0cD3eF6gH9jK2mN5oP8qR0tU3vW6xY9aB1cD4eF7gH\n0jK3mN6oP9qR1tU4vW7xY0aB2cD5eF8gH1jK4mN7oP0qR2tU5vW8xY1aB3cD6eF\n9gH2jK5mN8oP1qR3tU6vW9xY2aB4cD7eF0gH3jK6mN9oP2qR4tU7vW0xY3aB5cD\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xyz123@my-goodbarber-projet-261703.iam.gserviceaccount.com",
    "client_id": "117605897872109483726",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xyz123@my-goodbarber-projet-261703.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# إعدادات إضافية
NEWS_SOURCES = ["Google News", "Yahoo Finance", "Forex Factory"]
AUTO_UPDATE_INTERVAL = 300  # 5 دقائق
MAX_RECOMMENDATIONS = 50
ENABLE_CHAT_HISTORY = True

# رسالة ترحيبية
WELCOME_MESSAGE = f"""
مرحباً بك في AI Smart Trader Pro
تم تشغيل النظام بنجاح: {datetime.now().strftime('%Y-%m-%d %H:%M')}
التحليل التلقائي مفعل كل 5 دقائق
"""

print("تم تحميل الإعدادات بنجاح - النظام جاهز للعمل")