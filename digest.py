import email, getpass, imaplib, os, csv, sys, json, time, smtplib
from analyze_vulnerability_by_version import *
from bson import json_util
from pymongo import MongoClient, ReturnDocument
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
from email.parser import HeaderParser

################################################################
############### Global Variables ###############################
################################################################

clientAddress="nbalkiss@redhat.com" # Default value
client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
db = client['security_pilot']
severityThreshold=1

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
                    continue
                if part.get('Content-Disposition') is None:
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
    addedDocumentsObjectIds=[]
    for component in components:
        doc = db['components'].find_one_and_replace({'name':component['name']}, component, upsert=True, return_document=ReturnDocument.AFTER)
        addedDocumentsObjectIds.append(doc['_id'])
    return addedDocumentsObjectIds

#########################################################################
##### Generate temporary components.json local file from database #######
#########################################################################

def generateComponentsJSONFileFromDatabase():
    f=open('./components.json', 'w')
    components={}
    result = db["components"].find({},{'_id': 0})
    f.write(json_util.dumps(result))
    f.close()

#############################################################################
##### Analyze vulnerabilities in each submitted component, by version #######
#############################################################################

def generateVulnVersionDataByApplication(applicationIds):
    reportIds=[]
    for oid in applicationIds:
        component = db['components'].find_one({'_id':oid})
        reportId='component-data-'+component['name']
        reportIds.append(reportId)
        f = open(reportId+'.csv','w')
        f.write("group:artifact:version,CVE,severity,URL,nearestCleanVersion,latestCleanVersion,nearestRedHatVersion,latestRedHatVersion\n")        
        for dependency in component["dependencies"]:
            group=dependency["groupId"]
            artifact=dependency["artifactId"]
            version=dependency["version"]
            gavString=":".join([group,artifact,version])
            print 'Analyzing %s, %s, %s' % (group, artifact, version)
            try:
                result = findCleanVersion(group,artifact,version,severityThreshold)
                if not result:
                    continue
                redHatResult = findNearestAndLatestRedHatVersions(group,artifact,version)
                CVEs=":".join(str(securityIssue['reference']) for securityIssue in result['securityIssues'])
                severities=":".join(str(securityIssue['severity']) for securityIssue in result['securityIssues'])
                URLs=":".join(str(securityIssue['url']) for securityIssue in result['securityIssues'])
                f.write(",".join([gavString,CVEs,severities,URLs,str(result['nearestCleanVersion']),str(result['latestCleanVersion']),str(redHatResult['nearestRedHatVersion']),str(redHatResult['latestRedHatVersion'])]))
                f.write("\n")
            except ScanException, e:
                print str(e)
                f.write(gavString+', REQUIRES MANUAL ATTENTION -- Message: ' + str(e) + '\n')
        f.close()
    return reportIds

######################################################
##### Send reports as CSV attached to an email #######
######################################################

def sendReportsEmail(username, password, recipients, subject, text, reportIds):
    filenames = [reportId+".csv" for reportId in reportIds]
    msg = MIMEMultipart()
    msg['From'] = "redhat.jpmc.pilot@gmail.com" 
    msg['To'] = ", ".join(recipients) # Get this value from global variable assigned in parseEmails()
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    # Attach reports
    for file in filenames:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    for recipient in recipients:
        mailServer.sendmail(username, recipient, msg.as_string())
    mailServer.close()
