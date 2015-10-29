import groovy.xml.MarkupBuilder
import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText('{"jobs": {
    "struts": {
      "dependencies": {
        "1": {},
        "2": {}
      }
    },
    "struts2": {
      "dependencies": {
        "3": {},
        "4": {}
      }
    }
  }

}')




projects.jobs.each { job ->
    def xml = new MarkupBuilder()
    xml{
    modelVersion()
    groupId(job)
    artifactId()
    version()
    name()
    dependencies{
        job.dependencies.each { dep -> 
            dependency{
                groupId()
                artifactId()
                version()
            }
        }
    }
}
    
}