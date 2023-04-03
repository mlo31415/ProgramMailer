from __future__ import annotations
from typing import Optional

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from HelpersPackage import FindBracketedText, MessageLog, ReadListAsParmDict, GetParmFromParmDict
from Log import Log, LogError


# Search for a Program file and return its path.
# Look first in the location specified by path.  Failing that, look in defaultDir.  Failing that look in the CWD.

def main():
    parameters=ReadListAsParmDict('parameters.txt')
    if parameters is None or len(parameters) == 0:
        MessageLog(f"Can't open/read {os.getcwd()}/parameters.txt\nProgramMailer terminated.")
        exit(999)

    credentials=ReadListAsParmDict("Credentials.txt")
    if credentials is None or len(credentials) == 0:
        MessageLog(f"Can't open/read {os.getcwd()}/Credentials.txt\nProgramMailer terminated.")
        exit(999)

    # Open the mail file which was created using ProgramMailerAssembler
    allemailsPath=OpenProgramFile("Program participant schedules email.txt", parameters["PMADirectory"], ".")
    if not allemailsPath:
        MessageLog(f"Can't find 'Program participant schedules email.txt'\nProgramMailer terminated.")
        exit(999)
    with open(allemailsPath, "r") as file:
        allEmails=file.read()

    # Strip any leading lines which start with "#" and end \n or which are empty
    lines=allEmails.split("\n")
    allEmails=""
    starting=True
    for line in lines:
        if starting:
            if len(line) == 0:
                continue
            if line[0] == "#":
                continue
        starting=False
        allEmails+=line+"\n"


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

    returnAddress=GetParmFromParmDict(parameters, "ReturnAddress")
    mailFormat=GetParmFromParmDict(parameters, "MailFormat", "HTML")
    senderName=GetParmFromParmDict(parameters, "SenderName", "George")

    address=GetParmFromParmDict(credentials, "address")
    pw=GetParmFromParmDict(credentials, "password")

    numMessagesSent=0
    numMessagesFailed=0
    while len(allEmails.strip()) > 0:

        # Get the email address and message
        emailmessage, allEmails=FindBracketedText(allEmails, "email-message", stripHtml=False, stripWhitespace=True)
        if len(emailmessage) == 0:
            MessageLog(f"Tag <email-message> expected and not found.")
            break

        emailaddress, emailmessage=FindBracketedText(emailmessage, "email-address", stripHtml=False, stripWhitespace=True)
        if len(emailaddress) == 0:
            MessageLog(f"Tag <email-address> expected and not found.\nProgramMailer ended.")
            break
        content, emailmessage=FindBracketedText(emailmessage, "content", stripHtml=False, stripWhitespace=True)
        if len(content) == 0:
            MessageLog(f"Tag <content> expected and not found.\nProgramMailer ended.")
            break
        emailsubject, content=FindBracketedText(content, "email subject", stripHtml=False, stripWhitespace=True)
        if len(emailsubject) == 0:
            MessageLog(f"Tag <email-subject> expected and not found.\nProgramMailer ended.")
            break

        if Mail(senderName, address, pw, mailFormat, returnAddress, emailaddress, emailsubject, content):
            numMessagesSent+=1
        else:
            numMessagesFailed+=1

    Log(f"\n{numMessagesSent} messages sent.")
    if numMessagesFailed > 0:
        Log(f"\n{numMessagesFailed} messages failed.")


def Mail(senderName: str, senderAddress: str, password: str, mailFormat: str, returnAddr: str, recipientAddr: str, subject: str, content: str) -> bool:
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = senderName
    message['To'] = recipientAddr
    message['Subject'] = subject
    message.add_header('reply-to', returnAddr)
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
    sendErrors=session.sendmail(senderAddress, recipientAddr, text)
    session.quit()

    if len(sendErrors) > 0:
        LogError(f"Email to {recipientAddr} returned errors and probably failed")
        return False

    Log(f"Emailed: {recipientAddr}")
    return True


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