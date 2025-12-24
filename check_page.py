import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText

URL = "https://www.vio.hr/zona-za-medije/obavijesti/privremeni-prekid-u-opskrbi-vodom-zbog-radova/1833"

EMAIL_TO = "bozidaramagovca163@gmail.com"
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

def get_page_hash():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()

    text = r.text.strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), text


def send_email(content):
    msg = MIMEText(
        f"Došlo je do promjene na stranici:\n\n{URL}\n\n---\n\n{content[:2000]}"
    )
    msg["Subject"] = "🔔 Promjena na VIO obavijesti"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    new_hash, content = get_page_hash()

    if os.path.exists("last_hash.txt"):
        with open("last_hash.txt", "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    if new_hash != old_hash:
        send_email(content)
        with open("last_hash.txt", "w") as f:
            f.write(new_hash)
        print("Promjena pronađena – mail poslan.")
    else:
        print("Nema promjene.")


if __name__ == "__main__":
    main()
