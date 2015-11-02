import groovy.json.JsonSlurper
import groovy.xml.MarkupBuilder
def slurper=new JsonSlurper()
def projects=slurper.parseText(readFileFromWorkspace('jobs.json'))

projects.jobs.each {component, val ->
    job("${component}") {
	    triggers {
	        scm('*/15 * * * *')
	    }
	    steps {
	    	shell("wget -O pom.xml localhost:8080/jenkins/userContent/${component}-pom.xml")
	        maven{
	          goals('clean install')
	          mavenInstallation('Maven 3.3.3')
	        }
	        shell("curl -u admin:admin123 -X POST -H 'Content-Type: application/json' -d '{\"publicId\":\"${component}\",\"name\": \"${component}\",\"organizationId\":\"9e8ee77412304ec596d3588d9cb4f20b\"}' 'localhost:8070/api/v2/applications'")
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