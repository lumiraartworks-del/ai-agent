from __future__ import print_function
import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from agent_phase2 import handle_message  # ezt a fázis 2-ből hívjuk

# Gmail olvasásához és íráshoz szükséges engedélyek
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send"]

load_dotenv()

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def read_latest_email(service):
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
    messages = results.get("messages", [])
    if not messages:
        print("📭 Nincs új e-mail.")
        return None, None, None

    msg = service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
    msg_data = msg["payload"]["headers"]
    subject = next(h["value"] for h in msg_data if h["name"] == "Subject")
    sender = next(h["value"] for h in msg_data if h["name"] == "From")
    body_data = msg["payload"]["parts"][0]["body"]["data"]
    body = base64.urlsafe_b64decode(body_data).decode("utf-8")

    return sender, subject, body

def send_email(service, to, subject, message_text):
    message = EmailMessage()
    message.set_content(message_text)
    message["To"] = to
    message["From"] = "me"
    message["Subject"] = f"Re: {subject}"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(f"📤 E-mail elküldve: {send_message['id']}")

def main():
    service = get_gmail_service()
    sender, subject, body = read_latest_email(service)
    if not body:
        return

    print(f"📩 Üzenet {sender}-től: {subject}")
    print("Tartalom:", body)

    # AI válasz generálás (Fázis 2 logika)
    print("\n🤖 AI feldolgozás...")
    handle_message(body)  # ez kiírja a választ, e-mail küldést is intézi ha kell

    # Itt egyszerűsített: csak a választ küldjük vissza
    from io import StringIO
    import sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    handle_message(body)

    sys.stdout = old_stdout
    output = mystdout.getvalue()

    reply_line = output.split("🤖 AI válasza")[-1].strip()
    send_email(service, sender, subject, reply_line)

import time

if __name__ == "__main__":
    print("🤖 AI Email Agent elindult... (ellenőrzés 5 percenként)")
    while True:
        try:
            main()
            print("✅ Lefutott egy ciklus, várok 5 percet...")
        except Exception as e:
            print("⚠️ Hiba történt:", e)
        time.sleep(300)  # 5 perc