import xml.etree.cElementTree as etree
import json
import xml.dom.minidom
from gav import GAV
import urllib2


def verifyGAVInMavenCentral(gav):
	url = 'http://central.maven.org/maven2/%s/%s/%s/%s-%s.jar' % (gav.group.replace('.','/'), gav.artifact, gav.version, gav.artifact, gav.version)
	try:
		metadata = urllib2.urlopen(url)
		return True
	except urllib2.HTTPError, e:
		return False



components=json.loads(open('components.json').read())

for component in components:
	project=etree.Element('project')

	modelVersion=etree.Element('modelVersion')
	modelVersion.text='4.0.0'
	project.append(modelVersion)

	groupId=etree.Element('groupId')
	groupId.text='redHat'
	project.append(groupId)

	artifactId=etree.Element('artifactId')
	artifactId.text=component['name']
	project.append(artifactId)

	packaging=etree.Element('packaging')
	packaging.text="war"
	project.append(packaging)

	version=etree.Element('version')
	version.text="1.0-SNAPSHOT"
	project.append(version)

	name=etree.Element('name')
	name.text=component['name']
	project.append(name)

	dependencies=etree.Element('dependencies')
	project.append(dependencies)

	fi = open('invalid-components-'+component['name']+'.csv','w')

	for dep in component['dependencies']:
		group=dep['groupId']
		artifact=dep['artifactId']
		version=dep['version']
		if verifyGAVInMavenCentral(GAV(group,artifact,version)):
			dependency=etree.SubElement(dependencies, 'dependency')
			etree.SubElement(dependency, 'groupId').text=group
			etree.SubElement(dependency, 'artifactId').text=artifact
			etree.SubElement(dependency, 'version').text=version
			exclusions=etree.SubElement(dependency, 'exclusions')
			exclusion=etree.SubElement(exclusions, 'exclusion')
			etree.SubElement(exclusion, 'groupId').text='*'
			etree.SubElement(exclusion, 'artifactId').text='*'
		else:
			print "Excluding %s, %s, %s from generated POM" % (group, artifact, version)
			fi.write('%s,%s,%s\n' % (group, artifact, version))
	fi.close()	
	build=etree.SubElement(project,'build')
	plugins=etree.SubElement(build, 'plugins')
	plugin=etree.SubElement(plugins, 'plugin')
	etree.SubElement(plugin, 'groupId').text="org.apache.maven.plugins"
	etree.SubElement(plugin, 'artifactId').text="maven-war-plugin"
	etree.SubElement(plugin, 'version').text="2.6"
	configuration=etree.SubElement(plugin, 'configuration')
	etree.SubElement(configuration, 'failOnMissingWebXml').text="false"

	f = open(component['name']+'-pom.xml', 'w')
	xmlString = xml.dom.minidom.parseString(etree.tostring(project))
	f.write(xmlString.toprettyxml(indent="	"))



