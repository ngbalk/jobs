import requests, json
from requests.auth import HTTPBasicAuth

authenticationUrl="http://10.3.13.110:8070/rest/user/session"

reportsUrl = 'http://10.3.13.110:8070/rest/ci/componentDetails/aidw-viewer/list?componentIdentifier={%22format%22:%22maven%22,%22coordinates%22:{%22artifactId%22:%22spring-core%22,%22classifier%22:%22%22,%22extension%22:%22jar%22,%22groupId%22:%22org.springframework%22,%22version%22:%224.1.0.RELEASE%22}}&reportId=83f41e13b1874a7ea20abfc720c3a07e'

credentials = {'j_username':'sysadmin', 'j_password':'blackduck'}

session = requests.Session()

authResponse = session.post(authenticationUrl, auth=HTTPBasicAuth('admin', 'admin123'))

print authResponse

reportResponse = session.get(reportsUrl);
print reportResponse.text;
