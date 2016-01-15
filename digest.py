import email, getpass, imaplib, os, csv, sys, json, time
from analyze_vulnerability_by_version import *
from bson import json_util
from pymongo import MongoClient, ReturnDocument

################################################################
######### Download All Attachments from Gmail Server ###########
################################################################

def parseEmails():
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

    ######################################################################
    ########### Parse csv's and return dictionary of components ##########
    ######################################################################

    components = []
    for fn in os.listdir('attachments'):
        if fn.endswith(".csv"):
            component={}
            component['name']=fn.split(".csv")[0]
            component["dependencies"] = []
            f = open("attachments/"+fn, 'rt')
            try:
                reader = csv.reader(f)
                for row in reader:
                    dependency = {}
                    dependency["groupId"]=row[0]
                    dependency["artifactId"]=row[1]
                    dependency["version"]=row[2]
                    component["dependencies"].append(dependency)
                components.append(component)
            finally:
                f.close()
                os.remove("attachments/"+fn)
    os.rmdir("attachments")
    return components
    

###########################################################
########### Push components list to in database ###########
###########################################################

def storeComponents(components):
    client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
    db = client['security_pilot']
    addedDocumentsObjectIds=[]
    for component in components:
        doc = db['components'].find_one_and_replace({'name':component['name']}, component, upsert=True, return_document=ReturnDocument.AFTER)
        addedDocumentsObjectIds.append(doc['_id'])
    return addedDocumentsObjectIds

#########################################################################
##### Generate temporary components.json local file from database #######
#########################################################################

def generateComponentsJSONFileFromDatabase():
    client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
    db = client['security_pilot']
    if(os.path.isfile("components.json")):
        os.remove("components.json")
    f=open('./components.json', 'w')
    components={}
    result = db["components"].find({},{'_id': 0})
    f.write(json_util.dumps(result))
    f.close()

#############################################################################
##### Analyze vulnerabilities in each submitted component, by version #######
#############################################################################

def generateVulnVersionDataByApplication(applicationIds):
    client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
    db = client['security_pilot']
    for oid in applicationIds:
        component = db['components'].find_one({'_id':oid})
        f = open('component-data-'+component['name']+'.csv','w')
        f.write("group:artifact:version,nearestCleanVersion,latestCleanVersion,nearestRedHatVersion,latestRedHatVersion\n")        
        for dependency in component["dependencies"]:
            group=dependency["groupId"]
            artifact=dependency["artifactId"]
            version=dependency["version"]
            if not validateGAV(group,artifact,version):
                continue
            result = findCleanVersion(group,artifact,version)
            redHatResult = findNearestAndLatestRedHatVersion(group,artifact,version)
                f.write(",".join([result['gav'], str(result['nearestCleanVersion']['group'])+':'+str(result['nearestCleanVersion']['artifact'])+':'+str(result['nearestCleanVersion']['version']),str(result['latestCleanVersion']['group'])+':'+str(result['latestCleanVersion']['artifact'])+':'+str(result['latestCleanVersion']['version']),str(redHatResult['nearestRedHatVersion']['group'])+':'+str(redHatResult['nearestRedHatVersion']['artifact'])+':'+str(redHatResult['nearestRedHatVersion']['version']),str(redHatResult['latestRedHatVersion']['group'])+':'+str(redHatResult['latestRedHatVersion']['artifact'])+':'+str(redHatResult['latestRedHatVersion']['version'])]))
            f.write("\n")        
        f.close()
