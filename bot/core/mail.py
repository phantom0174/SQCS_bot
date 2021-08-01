import os
import yagmail


Account = os.environ.get("GMAIL_ACCOUNT")
Password = os.environ.get("GMAIL_PASSWORD")

yag = yagmail.SMTP(Account, Password)


async def send_email(to_account, subject, content):
    yag.send(
        to=to_account,
        subject=subject,
        contents=content
    )
