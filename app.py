import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

WBPSC_URL = "https://wbpsc.gov.in/"
ADVT_URL = "https://wbpsc.gov.in/advertisement.jsp"
KEYWORDS = ["polytechnic lecturer", "WBCS", "West Bengal Civil Service"]

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def fetch_wbpsc_notifications():
    try:
        res = requests.get(ADVT_URL, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        notifications = soup.find_all("a", href=True)
        matches = []

        for note in notifications:
            text = note.get_text(strip=True).lower()
            if any(kw in text for kw in [k.lower() for k in KEYWORDS]):
                matches.append(note.get_text(strip=True))
        return matches if matches else ["No new notification as of now."]
    except Exception as e:
        return [f"Error fetching notifications: {str(e)}"]

def save_to_pdf(lines, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in lines:
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(filename)

def send_email(body_lines, pdf_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "WBPSC/WBCS Notification Update"

    msg.attach(MIMEText("\n".join(body_lines), 'plain'))

    with open(pdf_path, 'rb') as f:
        attach = MIMEApplication(f.read(), _subtype='pdf')
        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(attach)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Checking for WBPSC/WBCS updates...")

    results = fetch_wbpsc_notifications()
    filename = "wbpsc_notifications.pdf"
    save_to_pdf(results, filename)
    send_email(results, filename)
    print("Email sent successfully!")

if __name__ == "__main__":
    main()
