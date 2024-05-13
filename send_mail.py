from email.message import EmailMessage
import ssl
import smtplib


def send_email():
    email_sender = "oetms2024@gmail.com"
    email_password = "oupv thzf eokx gnts"

    email_receiver = "oetms2024@gmail.com"
    subject = "New Harassment Report"
    body = "A new harassment report has been submitted. Please check the dashboard for more details."

    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, em.as_string())