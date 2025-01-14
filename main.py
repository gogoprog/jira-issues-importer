import getpass
from collections import namedtuple
import sys
from lxml import objectify
from project import Project
from importer import Importer
from labelcolourselector import LabelColourSelector


def read_xml_sourcefile(file_names):
    files = list()
    for file_name in file_names:
        all_text = open(file_name).read()
        files.append(objectify.fromstring(all_text))

    return files


file_names = sys.argv[1::]
all_xml_files = read_xml_sourcefile(file_names)

us = input('GitHub account name: ')
repo = input('GitHub project name: ')
default_labels = list(filter(None,
        [l.strip()
            for l in input('Default labels to apply (comma-separated): ').split(',')]))

Options = namedtuple("Options", "account repo")
opts = Options(account=us, repo=repo)

project = Project(default_labels)

for f in all_xml_files:
    for item in f.channel.item:
        project.add_item(item)

project.prettify()

start_from_issue = input('Start from [0 = beginning]: ') or 0

'''
Steps:
  1. Create any milestones
  2. Create any labels
  3. Create each issue with comments, linking them to milestones and labels
  4: Post-process all comments to replace issue id placeholders with the real ones
'''
importer = Importer(opts, project)
colourSelector = LabelColourSelector(project)

importer.import_milestones()

if int(start_from_issue) == 0:
    importer.import_labels(colourSelector)

importer.import_issues(int(start_from_issue))
importer.post_process_comments()
