import os
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import base64
import email
import imaplib

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_latest_pdf_attachment():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        mail_ids = data[0].split()
        for num in reversed(mail_ids):
            result, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            if msg.get_content_maintype() != "multipart":
                continue

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                if filename and filename.endswith(".pdf"):
                    return part.get_payload(decode=True), filename
        return None, "No PDF found"
    except Exception as e:
        return None, str(e)

def summarize_pdf():
    pdf_data, filename = get_latest_pdf_attachment()
    if not pdf_data:
        return f"Error: {filename}"

    # Save PDF temporarily
    temp_pdf_path = "latest.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_data)

    # Read PDF content (simple example using PyPDF2)
    import PyPDF2
    reader = PyPDF2.PdfReader(temp_pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Generate summary
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
            {"role": "user", "content": f"Summarize the following PDF content:\n\n{text[:4000]}"}
        ]
    )
    summary = response.choices[0].message.content
    return summary

# Gradio UI
iface = gr.Interface(fn=summarize_pdf, inputs=[], outputs="text", title="PDF Email Summarizer")
iface.launch()
