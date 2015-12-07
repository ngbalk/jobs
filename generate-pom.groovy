import groovy.xml.MarkupBuilder
import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText(new File("components.json").text)

projects.each {component, val ->
    def writer = new FileWriter(new File("${component}-pom.xml"))
    def xml = new MarkupBuilder(writer)
    xml.project{
        modelVersion("4.0.0")
        groupId("redhat")
        artifactId(component)
        packaging("war")
        version("1.0-SNAPSHOT")
        name(component)
        print val.dependencies
        dependencies{
            val.dependencies.each {dep-> 
                print dep
                dependency{
                    groupId(dep.groupId)
                    artifactId(dep.artifactId)
                    version(dep.version)
                }
            }
        }
        build{
            plugins{
                plugin{
                    groupId("org.apache.maven.plugins")
                    artifactId("maven-war-plugin")
                    version("2.6")
                    configuration{
                        failOnMissingWebXml("false")
                    }
                }
            }
        }
    }
}

