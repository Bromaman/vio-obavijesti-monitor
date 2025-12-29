import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ======================
# KONFIGURACIJA
# ======================

PAGES = {
    "VIO Obavijesti": "https://www.vio.hr/zona-za-medije/obavijesti/privremeni-prekid-u-opskrbi-vodom-zbog-radova/1833",
    "HEP Struja": "https://www.hep.hr/ods/bez-struje/19?dp=zagreb&el=ZG&datum=30.12.2025",
    "HEP Toplinarstvo": "https://www.hep.hr/toplinarstvo/krajnji-kupci/bez-toplinske-energije-1857/1857"
}

KEYWORDS = [
    "božidara magovca",
    "b. magovca",
    "travno",
    "travnog"
]

EMAIL_TO = "bozidaramagovca163@gmail.com"
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

STATUS_FILE = "status_found.txt"

# ======================
# POMOĆNE FUNKCIJE
# ======================

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)


def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r.text.lower()
    except Exception as e:
        print(f"Greška pri dohvaćanju {url}: {e}")
        return ""  # vraća prazan string ako ne može dohvatiti



# ======================
# GLAVNA LOGIKA
# ======================

def main():
    today = datetime.utcnow()
    weekday = today.weekday()  # Monday = 0

    found_matches = []

    for name, url in PAGES.items():
        content = fetch_page(url)

        for kw in K
