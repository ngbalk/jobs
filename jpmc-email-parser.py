# Make sure you have IMAP enabled in your gmail settings.
# Right now it won't download same file name twice even if their contents are different.

import email
import getpass, imaplib
import os
import sys
import csv
import json

################################################################
######### Download All Attachments from Gmail Server ###########
################################################################

Properties properties = new Properties()
properties.load(streamFileFromWorkspace('config.properties'))

detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')

userName = properties["gmailUsername"]
passwd = properties["gmailPassword"]

try:
    imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
    typ, accountDetails = imapSession.login(userName, passwd)
    if typ != 'OK':
        print 'Not able to sign in!'
        raise
    
    imapSession.select('[Gmail]/All Mail')
    typ, data = imapSession.search(None, 'ALL')
    if typ != 'OK':
        print 'Error searching Inbox.'
        raise
    
    # Iterating over all emails
    for msgId in data[0].split():
        typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            print 'Error fetching mail.'
            raise

        emailBody = messageParts[0][1]
        mail = email.message_from_string(emailBody)
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                # print part.as_string()
                continue
            if part.get('Content-Disposition') is None:
                # print part.as_string()
                continue
            fileName = part.get_filename()

            if bool(fileName):
                filePath = os.path.join(detach_dir, 'attachments', fileName)
                if not os.path.isfile(filePath) :
                    print fileName
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
    imapSession.close()
    imapSession.logout()
except :
    print 'Not able to download all attachments.'

################################################################################
########### Parse Attachments and Create Golden components.json File ###########
################################################################################

components = {}
for fn in os.listdir('attachments'):
    if fn.endswith(".csv"):
        #Create JSON Object
        component = {}
        f = open("attachments/"+fn, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                component["groupId"]=row[1]
                component["artifactId"]=row[2]
                component["version"]=row[3]
                components[row[0]]=component
        finally:
            f.close()
jsonData = json.dumps(components)

outFile=open('./components.json', 'w')
outFile.write(jsonData)


