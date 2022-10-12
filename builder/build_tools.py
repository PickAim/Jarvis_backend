import os
from datetime import datetime

from build_constants import _separator, element_name
from os import system as sys


def get_my_version() -> str:
    with(open(__file__.replace(os.path.basename(__file__), '') + 'build.properties', 'r') as properties):
        line = properties.readline()
        version = ''
        while line != "":
            name = line.split(_separator)[0]
            if name == element_name:
                version = line.split(_separator)[1]
                break
            line = properties.readline()
        if version == '':
            print('[ERROR] Invalid build.properties file format')
        version = version.replace('\n', '')
        return version


def publish_to_git():
    version = get_my_version()
    sys(f'git checkout -b release/{version}')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"[Auto: {datetime.now()}] publish {version}\"')
    sys(f'git push origin release/{version}')


def publish_to_git_with_comment(comment):
    version = get_my_version()
    sys(f'git checkout -b release/{version}')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"{comment}\"')
    sys(f'git push origin release/{version}')


def build():
    with(open(__file__.replace(os.path.basename(__file__), '') + 'build.properties', 'r') as properties,
         open(__file__.replace(os.path.basename(__file__), '') + 'dependencies.properties', 'r') as dependencies):
        sys('rd /s /q jarvis_db')
        props = properties.readlines()
        props_dict = {prop.split(_separator)[0]: prop.split(_separator)[1].replace('\n', '') for prop in props}
        depends = dependencies.readlines()
        depends_dict = {dependency.split(_separator)[0]: dependency.split(_separator)[1].replace('\n', '')
                        for dependency in depends}
        for prop_name in props_dict:
            if depends_dict.__contains__(prop_name):
                sys(f'git clone --branch release/{props_dict[prop_name]} {depends_dict[prop_name]}')
        sys('rd /s /q jarvis_db\\.git')
        sys('rd /s /q jarvis_db\\builder')
        sys('del /q jarvis_db\\.gitignore')
        sys('del /q jarvis_db\\README.md')
