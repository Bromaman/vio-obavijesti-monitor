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
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

STATUS_FILE = "status_found.txt"
WEEKLY_STATUS_FILE = "weekly_status.txt"


# ======================
# POMOĆNE FUNKCIJE
# ======================

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Mail poslan:", subject)
    except Exception as e:
        print("Greška pri slanju maila:", e)


def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r.text.lower(), True  # True = dostupna
    except Exception as e:
        print(f"Greška pri dohvaćanju {url}: {e}")
        return "", False  # False = nedostupna

# ======================
# GLAVNA LOGIKA
# ======================

def main():
    today = datetime.utcnow()
    weekday = today.weekday()  # Monday = 0

    found_matches = []
    unavailable_pages = []

    for idx, (name, url) in enumerate(PAGES.items(), start=1):
        content, available = fetch_page(url)
        if not available:
            unavailable_pages.append((idx, name))
            continue

        for kw in KEYWORDS:
            if kw in content:
                found_matches.append((name, kw, url))
                break

    previously_found = False
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                previously_found = f.read().strip() == "FOUND"
        except Exception:
            previously_found = False

    # 🔔 Ako su stranice nedostupne, pošalji mail odmah
    if unavailable_pages:
        body = "Sljedeće stranice nisu dostupne:\n\n"
        for idx, name in unavailable_pages:
            body += f"- Stranica {idx} ({name})\n"
        send_email(
            "⚠️ Greška: stranica nije dostupna",
            body
        )
        # NE izlazimo, jer možemo i dalje provjeriti dostupne stranice

    # 🔔 ODMAH JAVI AKO JE NEŠTO NAĐENO
    if found_matches and not previously_found:
        body = "Pronađeni su traženi pojmovi:\n\n"
        for name, kw, url in found_matches:
            body += f"- {name}: '{kw}'\n  {url}\n\n"

        send_email(
            "🚨 OBJAVLJENO – pronađena relevantna obavijest",
            body
        )

        try:
            with open(STATUS_FILE, "w") as f:
                f.write("FOUND")
        except Exception as e:
            print("Greška pri spremanju statusa:", e)

        return

    # 📅 TJEDNI STATUSNI MAIL – SAMO JEDNOM PO TJEDNU
    if not found_matches and weekday == 0:
        current_week = today.strftime("%Y-W%U")
        last_sent_week = None

        if os.path.exists(WEEKLY_STATUS_FILE):
            try:
                with open(WEEKLY_STATUS_FILE, "r") as f:
                    last_sent_week = f.read().strip()
            except Exception:
                last_sent_week = None

        if last_sent_week != current_week:
            body = (
                "Tjedni status – prošli tjedan NIJE objavljeno ništa vezano uz:\n"
                "- Božidara Magovca\n"
                "- B. Magovca\n"
                "- Travno / Travnog\n\n"
                "Provjerene stranice:\n"
            )
            for name, url in PAGES.items():
                body += f"- {name}: {url}\n"

            send_email(
                "📅 Tjedni status: nema objava za Travno / B. Magovca",
                body
            )

            try:
                with open(WEEKLY_STATUS_FILE, "w") as f:
                    f.write(current_week)
            except Exception as e:
                print("Greška pri spremanju tjednog statusa:", e)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Greška u skripti:", e)
