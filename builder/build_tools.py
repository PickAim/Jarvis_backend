import os
from subprocess import run, PIPE, STDOUT
from datetime import datetime

from build_constants import _separator, element_name, component_dir
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


def get_my_name(url: str) -> str:
    return url.split('/')[-1].split('.')[0]


def publish_to_git():
    version = get_my_version()
    saved_branch = run(f' git rev-parse --abbrev-ref HEAD',
              stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True).stdout.replace('\n', '')
    sys(f'git stash')
    out = run(f'git switch -c release/{version}',
              stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True).stdout
    if out.__contains__('fatal'):
        sys(f'git checkout release/{version}')
    sys(f'git rebase {saved_branch}')
    sys(f'git stash pop')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"[Auto: {datetime.now()}] publish {version}\"')
    sys(f'git push -f origin release/{version}')


def publish_to_git_with_comment(comment):
    version = get_my_version()
    saved_branch = run(f' git rev-parse --abbrev-ref HEAD',
                       stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True).stdout.replace('\n', '')
    sys(f'git stash')
    out = run(f'git switch -c release/{version}',
              stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True).stdout
    if out.__contains__('fatal'):
        sys(f'git checkout release/{version}')
    sys(f'git rebase {saved_branch}')
    sys(f'git stash pop')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"{comment}\"')
    sys(f'git push origin release/{version}')


def build():
    with(open(__file__.replace(os.path.basename(__file__), '') + 'build.properties', 'r') as properties,
         open(__file__.replace(os.path.basename(__file__), '') + 'dependency.properties', 'r') as dependencies):
        my_dir = __file__.replace(os.path.basename(__file__), '').replace('builder', '')
        print(f'Installing requirements for {my_dir}')
        run(f'pip install -r {os.path.join(my_dir, "requirements.txt")}',
            stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True)
        sys(f'rd /s /q {component_dir}')
        sys(f'mkdir {component_dir}')
        props = properties.readlines()
        props_dict = {}
        for prop in props:
            if prop.__contains__(_separator):
                props_dict[prop.split(_separator)[0]] = prop.split(_separator)[1].replace('\n', '')
        depends = dependencies.readlines()
        depends_dict = {dependency.split(_separator)[0]: dependency.split(_separator)[1].replace('\n', '')
                        for dependency in depends}
        for prop_name in props_dict:
            if depends_dict.__contains__(prop_name):
                dir_name = get_my_name(depends_dict[prop_name])
                sys(f'mkdir {os.path.join(component_dir, dir_name)}')
                sys(f'git clone --branch release/{props_dict[prop_name]} {depends_dict[prop_name]} '
                    f'{os.path.join(component_dir, dir_name)}')
                sys(f'rd /s /q {os.path.join(component_dir, dir_name)}\\.git')
                sys(f'del /q {os.path.join(component_dir, dir_name)}\\.gitignore')
                sys(f'del /q {os.path.join(component_dir, dir_name)}\\README.md')
                sys(f'python {os.path.join(component_dir, dir_name, "builder", "build.py")}')

                sys(f'rd /s /q {os.path.join(component_dir, dir_name)}\\builder')
