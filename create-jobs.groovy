import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText(readFileFromWorkspace('jobs.json'))

def organizationId="28dba0d94c7e452d9dd1a32e2a51f5f6"
def nexusUsername="admin"
def nexusPassword="admin123"
def blackduckUsername="sysadmin"
def blackduckPassword="blackduck"

projects.jobs.each {component, val ->
    job("${component}") {
	    steps {
	    	shell("wget -O pom.xml localhost:8080/jenkins/userContent/${component}-pom.xml")
	        maven{
	          goals('clean install')
	          mavenInstallation('Maven 3.3.3')
	        }
	        shell("curl -u ${nexusUsername}:${nexusPassword} -X POST -H 'Content-Type: application/json' -d '{\"publicId\":\"${component}\",\"name\": \"${component}\",\"organizationId\":\"${organizationId}\"}' 'localhost:8070/api/v2/applications'")
	        
//	        shell("curl -X POST --data 'j_username=sysadmin&j_password=blackduck' -i http://10.3.12.8:8080/j_spring_security_check")
//	        shell("curl -X POST --header 'Content-Type: application/vnd.blackducksoftware.project-1+json' --header 'Accept: application/json' -d '{description': '','name': '${component}','projectTier': 1,'source': 'CUSTOM'}' 'http://10.3.12.8:8080/api/projects'")

	        shell("wget -O scan.cli.zip http://10.3.12.8:8080/download/scan.cli.zip")
	        shell("unzip -o scan.cli.zip")
	        shell("bash scan.cli-*/bin/scan.cli.sh --username ${blackduckUsername} --password ${blackduckPassword} --host 10.3.12.8 --port 8080 target")
	    }
	    userContent("${component}-pom.xml",streamFileFromWorkspace("${component}-pom.xml"))
	    
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