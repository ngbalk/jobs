import groovy.json.JsonSlurper
import groovy.xml.MarkupBuilder
def slurper=new JsonSlurper()
def projects=slurper.parseText(readFileFromWorkspace('jobs.json'))

projects.jobs.each {component, val ->
	print "doing something"
    def writer = new FileWriter(new File("${component}-pom.xml"))
    def xml = new MarkupBuilder(writer)
    xml.project{
	    modelVersion()
	    groupId(component)
	    artifactId()
	    version()
	    name()
	    dependencies{
	        val.dependencies.each {dep-> 
	            dependency{
	                groupId(dep)
	                artifactId()
	                version()
	            }
	        }
	    }
	}
}

projects.jobs.each {component, val ->
    job("${component}") {
	    scm {
	        git('git://github.com/ngbalk/test-sonatype.git')
	    }
	    triggers {
	        scm('*/15 * * * *')
	    }
	    steps {
	        maven{
	          goals('clean install')
	          mavenInstallation('Maven 3.3.3')
	        }
	        shell("curl -u admin:admin123 -X POST -H 'Content-Type: application/json' -d '{\"publicId\":\"${component}\",\"name\": \"${component}\",\"organizationId\":\"e85ccd6ec0664bb4b5a5b490fe0829f6\"}' 'localhost:8070/api/v2/applications'")
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