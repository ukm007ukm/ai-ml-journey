import smtplib
import openai
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# For generating PDF
from fpdf import FPDF

# Load environment variables from .env
load_dotenv()

# Config
openai.api_key = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT = os.getenv("RECIPIENT")

# Step 1: Use OpenAI to generate update content
def generate_update():
    prompt = "Give me a short daily update on upcoming competitive exams in India."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Step 2: Create a PDF with the update
def create_pdf(content, filename="exam_update.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)

# Step 3: Send the email with PDF attached
def send_email(subject, body, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT
    msg.set_content(body)

    # Attach PDF
    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Run
if __name__ == "__main__":
    content = generate_update()
    create_pdf(content)
    send_email("Your Daily Exam Update", "Please find the attached PDF with today's update.", "exam_update.pdf")
