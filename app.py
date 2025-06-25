import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime
import time

# Configuration
sender_email = "007aiyt@gmail.com"
receiver_email = "7haveli@gmail.com"
app_password = "ckrfoxotcyxqzgrq"
smtp_server = "smtp.gmail.com"
smtp_port = 587

urls = {
    "WBPSC Polytechnic Lecturer": "https://psc.wb.gov.in/notification_announcement.jsp",
    "WBCS Notifications": "https://psc.wb.gov.in/notification_announcement.jsp"
}

def fetch_with_retries(url, retries=3, delay=5, timeout=100):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"[!] Attempt {attempt+1} failed. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                return f"Error fetching data after {retries} attempts: {e}"

def scrape_notifications():
    print("[*] Scraping WBPSC & WBCS pages...")
    messages = []

    for title, url in urls.items():
        html = fetch_with_retries(url)
        if html.startswith("Error"):
            messages.append(f"{title}:\n{html}")
            continue

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        matches = [
            link.get_text(strip=True)
            for link in links
            if "lecturer" in link.get_text(strip=True).lower() or
               "wbcs" in link.get_text(strip=True).lower()
        ]

        if matches:
            messages.append(f"{title}:\n" + "\n".join(matches))
        else:
            messages.append(f"{title}:\nNo new notification as of now.")

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
