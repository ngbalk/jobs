from digest import *

applications = parseEmails()
applicationIds=storeComponents(applications)
generateComponentsJSONFileFromDatabase()
generateVulnVersionDataByApplication(applicationIds)