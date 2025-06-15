import smtplib
from email.mime.text import MIMEText


def send_otp_email(receiver_email, otp):
    sender_email = "workflexnetwork@gmail.com"
    # Use App Password if Gmail 2FA enabled
    sender_password = "tqey tfmd ftxl faol"

    subject = "Your OTP Code"
    body = f"Thank you for using ShopEase Your OTP is: {otp} please dont share it with anyone"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print("Error sending OTP:", e)
        raise
