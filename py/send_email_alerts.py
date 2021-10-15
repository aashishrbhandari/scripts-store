from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders as Encoders

import smtplib
import os
import subprocess

import traceback
import datetime
import sys

class CustomMailer:

    ''' '''
    def __init__(self, userMessage):
        self.userMessage = userMessage

    ''' Get all the Config Data and Store it in Instance Variable '''
    def getConfigData(self):
        self.mailServer = "MAIL_Server"; # Mention SMTP Server IP or Domain, Incase of Gmail: smtp.gmail.com
        self.senderID = "a@e.com"; # Mention Email ID
        self.senderPasswd = "PASSWORD"; # Mention Email Account Password
        self.subject = "SafeSquid Performance Plots & Reports" # Mention Email Subject
        self.sendTo = "to@e.com"; # Send To Email ID/IDs... Add Multiple With , (COMMA) as Separator
        self.sendCC = "cc@e.com"; # Send CC Email ID/IDs... Add Multiple With , (COMMA) as Separator
        self.sendBCC = "bcc@e.com"; # Send BCC Email ID/IDs... Add Multiple With , (COMMA) as Separator
        self.folderName = "/usr/local/src/test1/"; # Directory Name Containing Files to Send.. Do Check the Size. Try Upload Files less than 10 MB


    ''' Create Mail Full Message Body '''
    def createMessage(self, displayMessage):

        ''' Creating the Mail Content '''
        messageData = MIMEMultipart();

        ''' Mail Header & Body '''
        messageData['Subject'] = self.subject;
        messageData['From'] = self.senderID;
        messageData['To'] = self.sendTo;

        if self.sendCC != "":
            print('[+] INSIDE IF != "" ->  sendCC Value: [+]', repr(self.sendCC))
            messageData['Cc'] = self.sendCC;

        print('[+] sendCC Value: [+]', repr(self.sendCC))

        if self.sendBCC != "":
            print('[+] INSIDE IF != "" ->  sendBCC Value: [+]', repr(self.sendBCC))
            messageData['Bcc'] = self.sendBCC;

        print('[+] sendBCC Value: [+]', repr(self.sendBCC))


        print("Message: ", type(displayMessage), displayMessage)

        messageData.attach(MIMEText(displayMessage,'html'));

        ''' File Attachments '''
        for file in os.listdir(self.folderName):

            fileWithPath = os.path.join(self.folderName, file);
            if os.path.isfile(fileWithPath):
                fileAttachment = open(fileWithPath, 'rb').read();
                sendFileData = MIMEBase('application', 'octet-stream');
                sendFileData.set_payload(fileAttachment);
                Encoders.encode_base64(sendFileData);
                sendFileData.add_header('Content-Disposition', 'attachment', filename=os.path.basename(fileWithPath))
                messageData.attach(sendFileData);
            else:
                print("Only Files inside the Mentioned Folder Path is Added as Attachment Sub-Dirs are Not Checked")
                print("Directory: Skipped: ", fileWithPath)

        return messageData

    '''  '''
    def getDecodedPasswd(self):
        # NO Security (V1), Will be Implemented Later
        return self.senderPasswd

    ''' '''
    def mailSender(self, messageData):

        ''' MAIL SENDING RELATED '''
        server = None
        try:
            server = smtplib.SMTP(self.mailServer, 587);
            server.starttls();
            decPassword = self.getDecodedPasswd();
            server.login(self.senderID, decPassword);
            '''
            Key thing is to add the Recipients as a list of email IDs in the Sendmail call.
            Send All your Data in String Format to Convert that use FUNCTION : as_string() of Class MIMEMultipart
            '''
            ''' Create Send List '''
            sendList = self.sendTo.split(',')

            if self.sendCC != "":
                for oneVal in self.sendCC.split(','):
                    sendList.append(oneVal)
            if self.sendBCC != "":
                for oneVal in self.sendBCC.split(','):
                    sendList.append(oneVal)

            print(sendList);

            server.sendmail(self.senderID, sendList, messageData.as_string());

        except Exception as e:
            exceptionTraceString = str(e)
            traceback.print_exc(file=sys.stdout)
            exceptionTime = datetime.date.today().ctime()

            print(exceptionTraceString)
            print(type(''.join(exceptionTraceString)))

            print('[+] Exception Trace Back Stored in File : sendMailer.log [+]')

        finally:
            print('[+] I am Finally Close the SMTP Connection [+]')
            #server.quit();

    ''' '''
    def doProcess(self):
        self.getConfigData()
        msgData = self.createMessage(self.userMessage)
        self.mailSender(msgData)


if __name__ == "__main__":

    print('[+] Starting Sending mail To Recipients [+]')

    try:
        displayMessage = sys.argv[1]
        print(displayMessage)
    except:
        raise Exception('[+] Please Provide Appropriate Arguments [+]')

        myMailer = CustomMailer(displayMessage);
        myMailer.doProcess()
