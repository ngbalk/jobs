def scanner={
  com.sonatype.insight.ci.hudson.PreBuildScan plugin="sonatype-clm-ci@2.14.2-01" {
        applicationSelectType {
          value 'list'
          applicationId 'testScan'
        }
        pathConfig ''
        failOnSecurityAlerts false
        failOnClmServerFailures false
        stageId 'build'
        username 'admin'
        password 'xoj2fUS2ClJB8TJePUwv/fcxMK881rz2S8jXmXEpDqk='
      }
}

job('struts-job') {
    scm {
        git('git://github.com/ngbalk/test-sonatype.git')
    }
    triggers {
        scm('*/15 * * * *')
    }
    steps {
        maven('clean package')
    }
    configure{ project ->
      (project / 'postbuilders').setValue(scanner)
}