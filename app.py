import os
import smtplib
import requests
import datetime
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from fpdf import FPDF
from email.message import EmailMessage

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

client = OpenAI(api_key=OPENAI_API_KEY)

# Fetch WBPSC and WBCS notification text
def get_wbpsc_updates():
    try:
        url = "https://wbpsc.gov.in/"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        latest = soup.find("marquee")
        return latest.get_text(strip=True) if latest else "No update found"
    except:
        return "Error fetching WBPSC updates."

# Fake UPSC update fetcher (replace with real logic if needed)
def get_upsc_current_affairs():
    return """India signs green hydrogen pact with EU. RBI keeps repo rate unchanged at 6.5%. Parliament to reconvene on July 10."""

# Generate summary using OpenAI
def generate_summary(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize this for a daily UPSC/WBPSC aspirant:"},
            {"role": "user", "content": text[:4000]}
        ]
    )
    return response.choices[0].message.content.strip()

# Create PDF
def create_pdf(content, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)

# Email with summary and PDF
def send_email(subject, body, attachment_path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content(body)

    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def main():
    date = datetime.date.today().strftime("%B %d, %Y")
    upsc_news = get_upsc_current_affairs()
    wbpsc_news = get_wbpsc_updates()

    combined = f"""📰 UPSC Current Affairs:\n{upsc_news}\n\n🏛 WBPSC/WBCS Notification:\n{wbpsc_news}"""
    summary = generate_summary(combined)

    create_pdf(summary, "Daily_Updates.pdf")
    send_email(
        subject=f"📬 Daily UPSC + WBPSC/WBCS Update — {date}",
        body=summary,
        attachment_path="Daily_Updates.pdf"
    )
    print("✅ Email sent successfully!")

if __name__ == "__main__":
    main()
