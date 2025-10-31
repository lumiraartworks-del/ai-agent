from flask import Flask, request, jsonify
from langdetect import detect
from openai import OpenAI
from dotenv import load_dotenv
import os

# Környezeti változók betöltése
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/message", methods=["POST"])
def message():
    data = request.json
    user_message = data.get("text", "")
    
    if not user_message:
        return jsonify({"error": "Nincs üzenet"}), 400
    
    # Nyelv felismerése
    lang = detect(user_message)
    
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
    
    ai_reply = response.choices[0].message.content
    return jsonify({"language": lang, "reply": ai_reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Railway vagy Render igényli a host="0.0.0.0"-t
    app.run(host="0.0.0.0", port=port)
