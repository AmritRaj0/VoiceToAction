import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, report):
    """ Sends an email with the extracted meeting report """
    
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        return "Error: Email configuration missing. Please check .env file."

    msg = MIMEText(report, "plain", "utf-8")  # Ensure correct encoding
    msg["Subject"] = "Your Meeting Report"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return "Report sent to your Email successfully!"
    except smtplib.SMTPAuthenticationError:
        return "Error: Invalid email credentials. Please check your email and app password."
    except smtplib.SMTPException as e:
        return f"Error: {str(e)}"
