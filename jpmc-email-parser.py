import email
import getpass, imaplib
import os
import sys
import csv
import json

################################################################
######### Download All Attachments from Gmail Server ###########
################################################################


# detach_dir = '.'
# if 'attachments' not in os.listdir(detach_dir):
#     os.mkdir('attachments')

# userName = "redhat.jpmc.pilot"
# passwd = "redhat123"

# try:
#     imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
#     typ, accountDetails = imapSession.login(userName, passwd)
#     if typ != 'OK':
#         print 'Not able to sign in!'
#         raise
    
#     imapSession.select('[Gmail]/All Mail')
#     typ, data = imapSession.search(None, '(UNSEEN)')
#     if typ != 'OK':
#         print 'Error searching Inbox.'
#         raise
    
#     # Iterating over all emails
#     for msgId in data[0].split():
#         typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
#         if typ != 'OK':
#             print 'Error fetching mail.'
#             raise

#         emailBody = messageParts[0][1]
#         mail = email.message_from_string(emailBody)
#         for part in mail.walk():
#             if part.get_content_maintype() == 'multipart':
#                 # print part.as_string()
#                 continue
#             if part.get('Content-Disposition') is None:
#                 # print part.as_string()
#                 continue
#             fileName = part.get_filename()

#             if bool(fileName):
#                 filePath = os.path.join(detach_dir, 'attachments', fileName)
#                 print fileName
#                 fp = open(filePath, 'wb')
#                 fp.write(part.get_payload(decode=True))
#                 fp.close()
#     imapSession.close()
#     imapSession.logout()
# except :
#     print 'Not able to download all attachments.'

################################################################################
########### Parse Attachments and Create Golden components.json File ###########
################################################################################


if(os.path.isfile("components.json")):
    print "components.json exists"
    with open('components.json') as data_file:    
        components = json.load(data_file)
else:
    print "components.json does not exit... starting from scratch"
    components = {}

for fn in os.listdir('attachments'):
    if fn.endswith(".csv"):
        
        components[fn.split(".csv")[0]] = {}
        components[fn.split(".csv")[0]]["dependencies"] = []
        
        f = open("attachments/"+fn, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                component = {}
                component["groupId"]=row[0]
                component["artifactId"]=row[1]
                component["version"]=row[2]

                #Add new component to golden component list
                components[fn.split(".csv")[0]]["dependencies"].append(component)
        finally:
            f.close()
jsonData = json.dumps(components)

outFile=open('./components.json', 'w')
outFile.write(jsonData)

##########################################
##### Clear Downloaded Attachments #######
##########################################

# filelist = [f for f in os.listdir("attachments")]
# for f in filelist:
#     os.remove("attachments/"+f)
# os.rmdir("attachments")


