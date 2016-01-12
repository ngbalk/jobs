import email
import getpass, imaplib
import os
import sys
import csv
import json
from analyze_vulnerability_by_version import findCleanVersion
from bson import json_util
from pymongo import MongoClient

################################################################
######### Download All Attachments from Gmail Server ###########
################################################################


detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')

userName = "redhat.jpmc.pilot"
passwd = "redhat123"

try:
    imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
    typ, accountDetails = imapSession.login(userName, passwd)
    if typ != 'OK':
        print 'Not able to sign in!'
        raise
    
    imapSession.select('[Gmail]/All Mail')
    typ, data = imapSession.search(None, '(UNSEEN)')
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
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
    imapSession.close()
    imapSession.logout()
except :
    print 'Not able to download all attachments.'

###############################################################
########### Parse Attachments and store in database ###########
###############################################################

client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
db = client['security_pilot']
for fn in os.listdir('attachments'):
    if fn.endswith(".csv"):
        componentName=fn.split(".csv")[0]
        component={}
        component[componentName] = {}
        component[componentName]["dependencies"] = []
        
        f = open("attachments/"+fn, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                dependency = {}
                dependency["groupId"]=row[0]
                dependency["artifactId"]=row[1]
                dependency["version"]=row[2]
                component[componentName]["dependencies"].append(dependency)
        finally:
            f.close()
            db['components'].replace_one({componentName: {"$exists": True}}, component, True)

            #############################################################################
            ##### Analyze vulnerabilities in each submitted component, by version #######
            #############################################################################
            f = open('vulnerabilityByVersion.csv','w')
            f.write("group:artifact:version,nearestCleanVersion,latestCleanVersion\n")
            results = []
            for dependency in component[componentName]["dependencies"]:
                results.append(findCleanVersion(dependency["groupId"], dependency["artifactId"], dependency["version"]))
            for result in results:
                if not result[result.keys()[0]]:
                    f.write(",".join([result.keys()[0], 'None', 'None']))
                else:
                    f.write(",".join([result.keys()[0], result[result.keys()[0]]['nearestCleanVersion']['group']+':'+result[result.keys()[0]]['nearestCleanVersion']['artifact']+':'+result[result.keys()[0]]['nearestCleanVersion']['version'],result[result.keys()[0]]['latestCleanVersion']['group']+':'+result[result.keys()[0]]['latestCleanVersion']['artifact']+':'+result[result.keys()[0]]['latestCleanVersion']['version']]))
                f.write("\n")
            f.close()

#########################################################################
##### Generate temporary components.json local file from database #######
#########################################################################

if(os.path.isfile("components.json")):
    os.remove("components.json")
outFile=open('./components.json', 'w')
components={}
for component in db["components"].find({},{'_id': 0}):
    for item in component:
        components[item]=component[item]
outFile.write(json_util.dumps(components))

###############################################################
##### Clear Downloaded Attachments and components.json  #######
###############################################################

filelist = [f for f in os.listdir("attachments")]
for f in filelist:
    os.remove("attachments/"+f)
os.rmdir("attachments")