import groovy.xml.MarkupBuilder
import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText(new File("jobs.json").text)

projects.jobs.each {component, val ->
    def writer = new FileWriter(new File("${component}-pom.xml"))
    def xml = new MarkupBuilder(writer)
    xml.project{
        modelVersion(val.modelVersion)
        groupId(val.groupId)
        artifactId(val.artifactId)
        version(val.version)
        name(val.name)
        dependencies{
            val.dependencies.each {dep-> 
                dependency{
                    groupId(dep.groupId)
                    artifactId(dep.artifactId)
                    version(dep.version)
                }
            }
        }
    }
}

