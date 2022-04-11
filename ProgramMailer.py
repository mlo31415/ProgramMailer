from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from HelpersPackage import FindAnyBracketedText, MessageLog, SelectFileBasedOnDebugger

def main():

    # Open the mail file which was created using ProgramMailerAssembler
    allEmails=""
    with open(SelectFileBasedOnDebugger("../ProgramMailAssembler", "Program participant schedules email.txt"), "r") as file:
        allEmails=file.read()

    # This file contains one or more emails.
    # An individual email is structures as:
    #   <email>
    #       <email-address>email address to mail to</email-address>
    #       <content>
    #           blah, blah, blah
    #       </content>
    #   </email>
    #
    # Indents are for clarity only
    # Newlines within the content are preserved
    # Lines beginning with "#" *outside* of the <email> blocks are ignored

    while len(allEmails) > 0:
        _, tag, content, remainder=FindAnyBracketedText(allEmails)
        if tag != "email-message":
            MessageLog(f"Top level tag<{tag}> encountered -- <email> expected.")
            return
        allEmails=remainder.strip()

        # Get the email address and message
        _, tag1, emailaddress, remainder=FindAnyBracketedText(content)
        if tag1 != "email-address":
            MessageLog(f"Top level tag<{tag}> encountered -- <email-address> expected.")
            return
        _, tag2, message, _=FindAnyBracketedText(remainder)
        if tag2 != "content":
            MessageLog(f"Top level tag<{tag}> encountered -- <content> expected.")
            return
        _, tag3, subject, body=FindAnyBracketedText(message)
        if tag3 != "email subject":
            MessageLog(f"email subject tag<{tag}> missing from <email message>.")
            return
        # sender_pass='moqwjlrbhoisqvkc'  # 'Prog3Analyzer'
        Mail('programtest2022@gmail.com', 'moqwjlrbhoisqvkc', 'mlo@baskerville.org', subject, body)


def Mail(senderAddress: str, password: str, recipient: str, subject: str, content: str) -> None:
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = senderAddress
    message['To'] = recipient
    message['Subject'] = subject
    #The body and the attachments for the mail
    message.attach(MIMEText(content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(senderAddress, password) #login with mail_id and password
    text = message.as_string()
    session.sendmail(senderAddress, recipient, text)
    session.quit()


if __name__ == "__main__":
    main()