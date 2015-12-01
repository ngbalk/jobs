import groovy.json.JsonSlurper

Properties properties = new Properties()
properties.load(streamFileFromWorkspace('config.properties'))

/* Black Duck Properties*/
def blackduckUsername=properties["blackduckUsername"]
def blackduckPassword=properties["blackduckPassword"]
def blackduckAddress=properties["blackduckAddress"]

/* Nexus Properties*/
def nexusUsername=properties["nexusUsername"]
def nexusPassword=properties["nexusPassword"]
def organizationId=properties["organizationId"]

/* Load components.json File */
def slurper=new JsonSlurper()
def projects=slurper.parseText(readFileFromWorkspace('components.json'))

/* Create New Component Build Job */
projects.each {component, val ->
    job("${component}") {
	    steps {
	    	shell("wget -O pom.xml localhost:8080/jenkins/userContent/${component}-pom.xml")
	        maven{
	        	goals('clean install')
	        	mavenInstallation('Maven 3.3.3')
	        }
/* Hit Sonatype to Initiate Scan */
	        shell("curl -u ${nexusUsername}:${nexusPassword} -X POST -H 'Content-Type: application/json' -d '{\"publicId\":\"${component}\",\"name\": \"${component}\",\"organizationId\":\"${organizationId}\"}' 'localhost:8070/api/v2/applications'")

/* Initiate Black Duck Scan */
//	        shell("curl -X POST --data 'j_username=${blackduckUsername}&j_password=${blackduckPassword}' -i http://${blackduckAddress}:8080/j_spring_security_check")
//	        shell("curl -X POST --header 'Content-Type: application/vnd.blackducksoftware.project-1+json' --header 'Accept: application/json' -d '{description': '','name': '${component}','projectTier': 1,'source': 'CUSTOM'}' 'http://${blackduckAddress}:8080/api/projects'")
	        shell("wget -O scan.cli.zip http://${blackduckAddress}:8080/download/scan.cli.zip")
	        shell("unzip -o scan.cli.zip")
	        shell("bash scan.cli-*/bin/scan.cli.sh --username ${blackduckUsername} --password ${blackduckPassword} --host ${blackduckAddress} --port 8080 target")
	    }
	    userContent("${component}-pom.xml",streamFileFromWorkspace("${component}-pom.xml"))

/* Configure Sonatype Plugin Settings*/
		configure { project ->
			project / publishers << 'com.sonatype.insight.ci.hudson.PostBuildScan'(plugin: 'sonatype-clm-ci@2.14.2-01') {
			applicationSelectType {
				value('list')
				applicationId("${component}")
			}
			pathConfig()
			failOnSecurityAlerts false
			failOnClmServerFailures false
			stageId('build')
			}
		}

	}
	queue("${component}")
}
