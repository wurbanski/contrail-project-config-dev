#!/usr/bin/env python
from __future__ import print_function
import sys
import yaml
import lxml
from lxml import etree

zuul_var_path = sys.argv[1]
manifest_path = sys.argv[2]

def dump_xml(node):
    return etree.tostring(node, pretty_print=True).decode()

def get_project(zuul_var, short_name):
    for p in zuul_var['projects']:
        if p['short_name'] == short_name:
            return p
    return None

with open(zuul_var_path, 'r') as zuul_var_file:
  zuul_var = yaml.load(zuul_var_file)

with open(manifest_path, 'r') as manifest_file:
  manifest = etree.parse(manifest_file)

project = manifest.find('//project[@name="{}"]'.format('contrail-controller'))
project.attrib['remote'] = 'ddd'

for remote in manifest.xpath('//remote'):
    remote.getparent().remove(remote)

remotes = {}
for project in zuul_var['projects']:
    remotes[project['canonical_hostname']] = etree.Element('remote', name=project['canonical_hostname'], fetch='file://' + zuul_var['executor']['src_root'] + '/' + project['canonical_hostname'] + '/Juniper')
    remotes[project['canonical_hostname']].tail = '\n'

for remote in remotes.values():
    manifest.getroot().insert(0,remote)

for project in manifest.xpath('//project'):
    name = project.attrib['name']
    zuul_project = get_project(zuul_var, name)
    project.attrib['remote'] = zuul_project['canonical_hostname']

with open(manifest_path, 'w') as manifest_file:
    manifest_file.write(dump_xml(manifest))
