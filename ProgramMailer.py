from __future__ import annotations
from typing import Optional

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from HelpersPackage import FindAnyBracketedText, MessageLog, ReadListAsParmDict


# Search for a Program file and return its path.
# Look first in the location specified by path.  Failing that, look in defaultDir.  Failing that look in the CWD.

def main():
    parameters=ReadListAsParmDict('parameters.txt')
    if parameters is None or len(parameters) == 0:
        MessageLog(f"Can't open/read {os.getcwd()}/parameters.txt\nProgramMailer terminated.")
        exit(999)

    # Open the mail file which was created using ProgramMailerAssembler
    allemailsPath=OpenProgramFile("Program participant schedules email.txt", parameters["PMADirectory"], ".")
    if not allemailsPath:
        MessageLog(f"Can't find 'Program participant schedules email.txt'\nProgramMailer terminated.")
        exit(999)
    with open(allemailsPath, "r") as file:
        allEmails=file.read()

    # This file contains one or more emails.
    # An individual email's structure is:
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

    returnAddress=parameters["ReturnAddress"]
    if not returnAddress:
        MessageLog(f"Can't find ReturnAddress value in parameters.txt\nProgramMailer terminated.")
        exit(999)
    mailFormat=parameters["MailFormat"]
    if not mailFormat:
        MessageLog(f"Can't find MailFormat value in parameters.txt\nProgramMailer terminated.")
        exit(999)

    while len(allEmails) > 0:
        _, tag, content, remainder=FindAnyBracketedText(allEmails)
        if tag != "email-message":
            MessageLog(f"Top level tag<{tag}> encountered -- <email> expected.\nProgramMailer ended.")
            return
        allEmails=remainder.strip()

        # Get the email address and message
        _, tag1, emailaddress, remainder=FindAnyBracketedText(content)
        if tag1 != "email-address":
            MessageLog(f"Top level tag<{tag}> encountered -- <email-address> expected.\nProgramMailer ended.")
            return
        _, tag2, message, _=FindAnyBracketedText(remainder)
        if tag2 != "content":
            MessageLog(f"Top level tag<{tag}> encountered -- <content> expected.\nProgramMailer ended.")
            return
        _, tag3, subject, body=FindAnyBracketedText(message)
        if tag3 != "email subject":
            MessageLog(f"email subject tag<{tag}> missing from <email message>.\nProgramMailer ended.")
            return
        # sender_pass='moqwjlrbhoisqvkc'  # 'Prog3Analyzer'
        Mail(returnAddress, 'programtest2022@gmail.com', 'moqwjlrbhoisqvkc', mailFormat, emailaddress, subject, body)


def Mail(returnAddress: str, senderAddress: str, password: str, mailFormat: str, recipient: str, subject: str, content: str) -> None:
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = returnAddress
    message['To'] = recipient
    message['Subject'] = subject
    #The body and the attachments for the mail

    if mailFormat.lower().strip() == "html":
        message.attach(MIMEText(content, 'html'))
    else:
        message.attach(MIMEText(content, 'plain'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(senderAddress, password) #login with mail_id and password
    text = message.as_string()
    session.sendmail(senderAddress, recipient, text)
    session.quit()

def OpenProgramFile(fname: str, path: str, defaultDir: str, report=True) -> Optional[str]:
    if fname is None:
        MessageLog(f"OpenProgramFile: fname is None, {path=}")
        return None

    if path is not None:
        pathname=os.path.join(path, fname)
        if os.path.exists(pathname):
            return pathname

    pathname=os.path.join(defaultDir, fname)
    if os.path.exists(pathname):
        return pathname

    if os.path.exists(fname):
        return fname

    if report:
        if defaultDir != "." and path != ".":
            MessageLog(f"Can't find '{fname}': checked '{path}', '{defaultDir}' and './'")
        elif path != ".":
            MessageLog(f"Can't find '{fname}': checked '{path}' and './'")
        else:
            MessageLog(f"Can't find '{fname}': checked './'")

    return None



if __name__ == "__main__":
    main()