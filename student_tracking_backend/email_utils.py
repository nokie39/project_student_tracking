import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(to_email: str, otp_code: str):
    # ດຶງຄ່າຈາກ Environment Variables (ທີ່ເຮົາຕັ້ງໃນ Cloud Run)
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    smtp_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("MAIL_PORT", 587))

    if not sender_email or not sender_password:
        print("⚠️ Email credentials not set. Skipping email.")
        return False

    # ສ້າງຫົວຂໍ້ ແລະ ເນື້ອຫາອີເມວ
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🔐 ລະຫັດ OTP ຂອງທ່ານ: {otp_code}"
    message["From"] = sender_email
    message["To"] = to_email

    # HTML Template ງາມໆ
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50; text-align: center;">ລະຫັດຢືນຢັນຕົວຕົນ (OTP)</h2>
          <p style="font-size: 16px; color: #555;">ສະບາຍດີ,</p>
          <p style="font-size: 16px; color: #555;">ລະຫັດ OTP ສຳລັບເຂົ້າສູ່ລະບົບ Student Tracking ຂອງທ່ານແມ່ນ:</p>
          
          <div style="background-color: #e3f2fd; color: #1976d2; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; border-radius: 8px; margin: 20px 0;">
            {otp_code}
          </div>

          <p style="font-size: 14px; color: #888; text-align: center;">ລະຫັດນີ້ຈະໝົດອາຍຸພາຍໃນ 5 ນາທີ.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #aaa; text-align: center;">School Tracking System</p>
        </div>
      </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    try:
        # ເຊື່ອມຕໍ່ຫາ Gmail Server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # ເຂົ້າລະຫັດການສົ່ງ
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
            
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False