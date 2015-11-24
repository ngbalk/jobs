import groovy.json.JsonSlurper

Properties properties = new Properties()
properties.load(streamFileFromWorkspace('config.properties'))
def blackduckUsername=properties["blackduckUsername"]
def blackduckPassword=properties["blackduckPassword"]
def blackduckAddress=properties["blackduckAddress"]

def slurper=new JsonSlurper()
def projects=slurper.parseText(readFileFromWorkspace('jobs.json'))
projects.jobs.each {component, val ->
    job("${component}") {
	    steps {
	    	shell("wget -O pom.xml localhost:8080/jenkins/userContent/${component}-pom.xml")
	        maven{
	          goals('clean install')
	          mavenInstallation('Maven 3.3.3')
	        }
//	        shell("curl -X POST --data 'j_username=${blackduckUsername}&j_password=${blackduckPassword}' -i http://${blackduckAddress}:8080/j_spring_security_check")
//	        shell("curl -X POST --header 'Content-Type: application/vnd.blackducksoftware.project-1+json' --header 'Accept: application/json' -d '{description': '','name': '${component}','projectTier': 1,'source': 'CUSTOM'}' 'http://${blackduckAddress}:8080/api/projects'")
	        shell("wget -O scan.cli.zip http://${blackduckAddress}:8080/download/scan.cli.zip")
	        shell("unzip -o scan.cli.zip")
	        shell("bash scan.cli-*/bin/scan.cli.sh --username ${blackduckUsername} --password ${blackduckPassword} --host ${blackduckAddress} --port 8080 target")
	    }
	    userContent("${component}-pom.xml",streamFileFromWorkspace("${component}-pom.xml"))
	}
	queue("${component}")
}