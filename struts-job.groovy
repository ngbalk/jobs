job('struts-job') {
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