from digest import *

applications = parseEmails()
applicationIds=storeComponents(applications)
generateComponentsJSONFileFromDatabase()
reportIds=generateVulnVersionDataByApplication(applicationIds)
sendReportsEmail("redhat.jpmc.pilot@gmail.com", "redhat123", ["nbalkiss@redhat.com"], "Vulernability Report", "See attached report.", reportIds)

# TODO
# Have the report sender respond to the email address that initiated the report.
# Make it possible to toggle the threshold that we want to allow as a vulnerability
# Refactor out dictinary creation in findNearestandLatestCleanVersions and findNearestandLatestRedHatVersions