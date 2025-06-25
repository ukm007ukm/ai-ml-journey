import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import datetime

# Email config
EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'  # Use Gmail app password
EMAIL_RECEIVER = 'recipient_email@gmail.com'

def fetch_wbpsc_polytechnic():
    print("Checking WBPSC Polytechnic Lecturer notifications...")
    url = "https://wbpsc.gov.in"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        notifications = soup.find_all('marquee')
        text = '\n'.join(m.text.strip() for m in notifications if 'polytechnic' in m.text.lower())
        return text if text else "No Polytechnic Lecturer notification at this time."
    except Exception as e:
        return f"Failed to fetch WBPSC Polytechnic: {str(e)}"

def fetch_wbcs():
    print("Checking WBCS notifications...")
    url = "https://wbpsc.gov.in"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        notifications = soup.find_all('marquee')
        text = '\n'.join(m.text.strip() for m in notifications if 'wbcs' in m.text.lower())
        return text if text else "No WBCS notification at this time."
    except Exception as e:
        return f"Failed to fetch WBCS: {str(e)}"

def generate_pdf(content):
    print("Generating PDF...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    filename = "notifications.pdf"
    pdf.output(filename)
    return filename

def send_email(content, attachment_path):
    print("Sending email...")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"WBPSC/WBCS Notification Update - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    msg.attach(MIMEText(content, 'plain'))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="notifications.pdf")
        part['Content-Disposition'] = 'attachment; filename="notifications.pdf"'
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    print("Starting scheduled check...")
    polytechnic = fetch_wbpsc_polytechnic()
    wbcs = fetch_wbcs()

    combined = f"{polytechnic}\n\n{wbcs}"
    pdf_path = generate_pdf(combined)
    send_email(combined, pdf_path)

if __name__ == "__main__":
    main()
