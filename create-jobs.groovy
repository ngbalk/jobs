import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText('{"jobs":["struts","stuts2", "strutsPoop"]}')

projects.jobs.each { jobName ->
    job('struts-job: ${jobName}') {
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
	        shell('curl -u admin:admin123 -X POST -H "Content-Type: application/json" -d \'{"publicId":"${jobName}","name": "${jobName}","organizationId":"c33c55b5822d42ec92cdc75904438132"}\' \'localhost:8070/api/v2/applications\'')
	    }
	    
	    configure { project ->
	        project / publishers << 'com.sonatype.insight.ci.hudson.PostBuildScan'(plugin: 'sonatype-clm-ci@2.14.2-01') {
	          applicationSelectType {
	            value('list')
	            applicationId('testScan')
	          }
	          pathConfig()
	          failOnSecurityAlerts false
	          failOnClmServerFailures false
	          stageId('build')
	          username('admin')
	          password('xoj2fUS2ClJB8TJePUwv/fcxMK881rz2S8jXmXEpDqk=')
	        }
	    }
	}
}