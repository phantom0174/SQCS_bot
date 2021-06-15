import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

Account = os.environ.get("GmailAccount")
Password = os.environ.get("GmailPassword")

# server setup
smtpserver = smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtpserver.ehlo()
smtpserver.login(Account, Password)

# only used for shutting down
# smtpserver.quit()


async def send_email(to_account, subject, content):
    mail = MIMEMultipart()
    mail['From'] = Account
    mail['To'] = to_account
    mail['Subject'] = Header(subject, 'utf-8')

    # content encoding
    content = MIMEText(content, "plain", "utf-8")
    mail.attach(content)

    smtpserver.sendmail(Account, to_account, mail.as_string())
