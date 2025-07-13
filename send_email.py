import smtplib
from email.mime.text import MIMEText

sender = "xuankhai191@gmail.com"
receiver = "xuankhai191@gmail.com"
subject = "✅ Todolist Auto Deploy - Thành công"
body = "🚀 Dự án Todolist đã được deploy thành công từ GitLab CI/CD lên EC2."

# Gmail App Password
password = "xgnbkhvlulodwcgw"  # Gõ liền, không có khoảng trắng

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender
msg["To"] = receiver

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
