import smtplib
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os
from datetime import datetime
from email.message import EmailMessage

# ------------------------
# CONFIGURATION
# ------------------------
EMAIL_USER = os.getenv("EMAIL_USER") or "your_email@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS") or "your_app_password"
EMAIL_TO = os.getenv("EMAIL_TO") or "your_email@gmail.com"  # where to send

# ------------------------
# FUNCTIONS
# ------------------------

def fetch_notifications():
    notifications = []

    try:
        # WBPSC Polytechnic Lecturer
        wbpsc_url = 'https://wbpsc.gov.in/'
        wbpsc_res = requests.get(wbpsc_url, timeout=15)
        soup = BeautifulSoup(wbpsc_res.text, 'html.parser')
        if 'polytechnic lecturer' in soup.text.lower():
            notifications.append("Polytechnic Lecturer notification found.")

        # WBCS
        wbcs_url = 'https://wbpsc.gov.in/'
        wbcs_res = requests.get(wbcs_url, timeout=15)
        if 'wbcs' in wbcs_res.text.lower():
            notifications.append("WBCS notification found.")

    except Exception as e:
        notifications.append(f"Error fetching notifications: {e}")

    if not notifications:
        notifications.append("No new notifications as of now.")

    return notifications

def generate_pdf(notifications):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="WBPSC & WBCS Notification Update", ln=1, align='C')
    pdf.cell(200, 10, txt=datetime.now().strftime("%Y-%m-%d %H:%M"), ln=2, align='C')
    pdf.ln(10)

    for note in notifications:
        pdf.multi_cell(0, 10, note)

    file_path = "notification_update.pdf"
    pdf.output(file_path)
    return file_path

def send_email(notifications, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = 'WBPSC & WBCS Notification Update'
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg.set_content("\n".join(notifications))

    with open(pdf_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ------------------------
# MAIN
# ------------------------

if __name__ == "__main__":
    notes = fetch_notifications()
    pdf_file = generate_pdf(notes)
    send_email(notes, pdf_file)
    print("✅ Notification email sent.")
