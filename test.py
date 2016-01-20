from analyze_vulnerability_by_version import *
from gav import GAV
from digest import *
from pymongo import *
import json
gav=GAV('commons-collections','commons-collections','3.2.1')
# print findNearestAndLatestRedHatVersions('commons-collections','commons-collections','3.2')
# result= findCleanVersion('xalan','xalan','2.7.0', 0)
# CVEs=":".join(securityIssue['reference'] for securityIssue in result['securityIssues'])
# severities=":".join(str(securityIssue['severity']) for securityIssue in result['securityIssues'])
# URLs=":".join(securityIssue['url'] for securityIssue in result['securityIssues'])
# print CVEs, severities, URLs



# client = MongoClient('mongodb://system:redhat123@ds039175.mongolab.com:39175/security_pilot')
# db = client['security_pilot']
# componentIds=db['components'].find({},{'_id':1})
# arr=[]
# for componentId in componentIds:
# 	arr.append(componentId['_id'])
# generateVulnVersionDataByApplication(arr)


print json.loads(getVulnerabilityData(gav))


