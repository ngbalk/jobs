import groovy.xml.MarkupBuilder
import groovy.json.JsonSlurper

def slurper=new JsonSlurper()
def projects=slurper.parseText(new File("components.json").text)

projects.each {component ->
    def writer = new FileWriter(new File("${component.name}-pom.xml"))
    def xml = new MarkupBuilder(writer)
    xml.project{
        modelVersion("4.0.0")
        groupId("redhat")
        artifactId(component.name)
        packaging("war")
        version("1.0-SNAPSHOT")
        name(component.name)
        dependencies{
            component.dependencies.each {dep-> 
                dependency{
                    groupId(dep.groupId)
                    artifactId(dep.artifactId)
                    version(dep.version)
                    exclusions{
                        exclusion{
                            groupId('*')
                            artifactId('*')
                        }
                    }
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
