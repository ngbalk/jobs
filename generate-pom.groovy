import groovy.xml.MarkupBuilder
import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText('{"jobs":{"struts":{"dependencies":["1","2"]},"struts2":{"dependencies":["3","4"]}}}')

projects.jobs.each {component, val ->
    def writer = new FileWriter(new File("${component}-pom.xml"))
    def xml = new MarkupBuilder(writer)
    xml.project{
        modelVersion()
        groupId(component)
        artifactId()
        version()
        name()
        dependencies{
            val.dependencies.each {  dep-> 
                dependency{
                    groupId(dep)
                    artifactId()
                    version()
                }
            }
        }
    }
//userContent("${component}-pom.xml",streamFileFromWorkspace("${component}-pom.xml"))
}

