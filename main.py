from langdetect import detect
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Üzenet bekérése
user_message = input("Írd be az ügyfél üzenetét: ")

# Nyelv felismerése
lang = detect(user_message)
print(f"🌐 Felismert nyelv: {lang}")

# AI válasz generálása
prompt = f"""
Te egy ügyfélszolgálati asszisztens vagy.
Feladatod, hogy válaszolj ugyanazon a nyelven, mint az ügyfél.
Ügyfél üzenete: {user_message}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
)

print("\n🤖 AI válasza:")
print(response.choices[0].message.content)