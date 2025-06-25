import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime

# Config
sender_email = "007aiyt@gmail.com"
receiver_email = "7haveli@gmail.com"
app_password = "ckrfoxotcyxqzgrq"
smtp_server = "smtp.gmail.com"
smtp_port = 587

def scrape_indgovtjobs():
    print("[*] Scraping indgovtjobs.in...")
    url = "https://www.indgovtjobs.in/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    keywords = ["wbpsc", "lecturer", "wbcs", "west bengal"]
    links = soup.find_all("a", href=True)

    matches = []
    for link in links:
        text = link.get_text(strip=True).lower()
        if any(keyword in text for keyword in keywords):
            matches.append(link.get_text(strip=True) + " - " + link["href"])

    if not matches:
        return "No relevant WBPSC/WBCS notifications found as of now."
    return "\n".join(matches)

def generate_pdf(content, filename="notification.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(filename)

def send_email(subject, body, attachment_path):
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
    except Exception as e:
        print("[!] Failed to send email:", e)

if __name__ == "__main__":
    print("[*] Running script at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    content = scrape_indgovtjobs()
    generate_pdf(content)
    send_email("WBPSC/WBCS Notification Update", content, "notification.pdf")
