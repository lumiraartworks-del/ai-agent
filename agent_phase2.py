from openai import OpenAI
from langdetect import detect
from deep_translator import GoogleTranslator
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# 🔹 Betöltjük a környezeti változókat
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate_to_english(text):
    lang = detect(text)
    if lang == "en":
        return text, lang
    translated = GoogleTranslator(source='auto', target='en').translate(text)
    return translated, lang

def translate_back_to_original(text, original_lang):
    if original_lang == "en":
        return text
    return GoogleTranslator(source='en', target=original_lang).translate(text)

def generate_reply(user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional multilingual customer support agent."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

def is_confident(user_message, ai_reply):
    check = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a QA agent. Decide if this support reply is confident and complete. Reply YES or NO."},
            {"role": "user", "content": f"Message: {user_message}\nAnswer: {ai_reply}"}
        ]
    )
    return "YES" in check.choices[0].message.content.upper()

def send_escalation_email(original_message, ai_reply):
    msg = MIMEText(f"⚠️ ESCALATION NEEDED\n\nMessage:\n{original_message}\n\nAI Reply:\n{ai_reply}")
    msg["Subject"] = "AI Escalation Alert"
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = os.getenv("ADMIN_EMAIL")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)

def handle_message(message):
    print("💬 Üzenet érkezett:", message)
    
    # 1️⃣ Nyelvfelismerés + fordítás
    message_en, original_lang = translate_to_english(message)

    # 2️⃣ Válasz generálása
    reply_en = generate_reply(message_en)

    # 3️⃣ Bizalom ellenőrzése
    confident = is_confident(message_en, reply_en)

    # 4️⃣ Visszafordítás eredeti nyelvre
    reply_final = translate_back_to_original(reply_en, original_lang)

    # 5️⃣ Ha nem biztos, továbbítás embernek
    if not confident:
        send_escalation_email(message, reply_final)
        print("🚨 Az AI bizonytalan volt, e-mailt küldött neked.")
    else:
        print(f"🤖 AI válasza ({original_lang}): {reply_final}")

# --- Teszt üzenet ---
handle_message("Bonjour, je n’ai pas reçu ma commande.")
