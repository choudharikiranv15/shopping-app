from flask_mail import Message
from core.mail_config import mail


def send_otp_email(email, otp):
    print("✅ Using updated send_otp_email()")  # Debug log

    subject = "🔐 ShopEase - Your OTP Code"

    # Plain-text fallback
    body = (
        f"Thank you for visiting ShopEase!\n\n"
        f"🧾 Your One-Time Password (OTP) is: {otp}\n\n"
        f"⚠️ Do not share this code with anyone.\n"
        f"This OTP is valid for a short time only.\n\n"
        f"Happy Shopping!\n"
        f"— Team ShopEase"
    )

    # HTML content
    html_body = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; border: 1px solid #ddd;">
        <h2 style="color: #4CAF50;">🛒 Welcome to <span style="color:#000">ShopEase</span></h2>
        <p>Hi there,</p>
        <p><strong>Your One-Time Password (OTP) is:</strong></p>
        <h1 style="letter-spacing: 4px; background-color: #e8f5e9; padding: 12px 20px; border-radius: 8px; display: inline-block; color: #2e7d32;">{otp}</h1>
        <p style="margin-top: 20px;">Please enter this OTP to verify your identity. This code is valid for a short time and should not be shared with anyone.</p>
        <hr style="margin: 30px 0;">
        <p style="font-size: 0.9em; color: #555;">Need help? Reach us at support@shopease.com</p>
        <p style="font-size: 0.9em; margin-top: 30px;">— Team ShopEase</p>
    </div>
    """

    msg = Message(subject=subject, recipients=[email])
    msg.body = body
    msg.html = html_body

    try:
        mail.send(msg)
        print(f"✅ OTP email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send OTP email to {email}: {e}")
