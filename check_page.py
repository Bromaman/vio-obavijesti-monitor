import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

URL = "https://www.vio.hr/zona-za-medije/obavijesti/privremeni-prekid-u-opskrbi-vodom-zbog-radova/1833"

KEYWORD = "travno"  # tražimo case-insensitive

EMAIL_TO = "bozidaramagovca163@gmail.com"
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

HASH_FILE = "last_hash.txt"
STATUS_FILE = "travno_status.txt"  # pamti je li Travno već pronađeno


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)


def get_page_content():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text


def main():
    content = get_page_content()
    content_lower = content.lower()

    today = datetime.utcnow()
    weekday = today.weekday()  # Monday = 0

    travno_found = KEYWORD in content_lower

    previously_found = False
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            previously_found = f.read().strip() == "FOUND"

    # ✅ SLUČAJ 1: Travno se pojavilo (i još nije javljeno)
    if travno_found and not previously_found:
        send_email(
            "🚨 OBJAVLJENO: Travno",
            f"Na stranici se pojavila riječ 'Travno'.\n\n{URL}"
        )
        with open(STATUS_FILE, "w") as f:
            f.write("FOUND")
        return

    # 📅 SLUČAJ 2: NEMA Travna → ponedjeljak popodne
    # GitHub Actions radi u UTC → 15–18 UTC ≈ popodne u HR
    if not travno_found and weekday == 0:
        send_email(
            "ℹ️ Travno još nije objavljeno",
            f"Do sada se riječ 'Travno' još nije pojavila na stranici.\n\n{URL}"
        )


if __name__ == "__main__":
    main()
