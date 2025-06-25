import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime

# Configuration
sender_email = "007aiyt@gmail.com"
receiver_email = "7haveli@gmail.com"
app_password = "ckrfoxotcyxqzgrq"
smtp_server = "smtp.gmail.com"
smtp_port = 587

def scrape_notifications():
    print("[*] Scraping WBPSC & WBCS pages...")

    urls = {
        "WBPSC Polytechnic Lecturer": "https://psc.wb.gov.in/notification_announcement.jsp",
        "WBCS Notifications": "https://psc.wb.gov.in/notification_announcement.jsp"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    messages = []

    for title, url in urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.find_all("a", href=True)
            matches = [link.get_text(strip=True) for link in links if "lecturer" in link.text.lower() or "wbcs" in link.text.lower()]

            if matches:
                messages.append(f"{title}:\n" + "\n".join(matches))
            else:
                messages.append(f"{title}:\nNo WBPSC/WBCS-specific notifications found as of now.")

        except Exception as e:
            messages.append(f"{title}:\nError fetching data: {e}")

    return "\n\n".join(messages)

def generate_pdf(content, filename="notification.pdf"):
    print("[*] Generating PDF...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(filename)

def send_email(subject, body, attachment_path):
    print("[*] Sending email...")
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    if not body.strip():
        body = "No notifications found."
    msg.attach(MIMEText(body, "plain"))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="notification.pdf")
        part["Content-Disposition"] = 'attachment; filename="notification.pdf"'
        msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        print("[✓] Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("[!] SMTP Authentication error:", e)
    except Exception as e:
        print("[!] Failed to send email:", e)

if __name__ == "__main__":
    print("[*] Running notification script at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = scrape_notifications()
    generate_pdf(message)
    send_email("WBPSC/WBCS Notification Update", message, "notification.pdf")
