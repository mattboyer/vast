from . import Command, CLI_subcmd
from .. import PROJECT_NAME

import pip


@CLI_subcmd('version')
class VersionCmd(Command):
    '''
    Displays version information
    '''

    def run(self, arg_ns):
        versions = {}
        for pkg_metadata in pip.get_installed_distributions():
            versions[pkg_metadata.project_name] = pkg_metadata
        print("Running {0} {1}\n".format(
            PROJECT_NAME, versions[PROJECT_NAME].version
        ))

        for dep in sorted(
            versions[PROJECT_NAME].requires(),
            key=lambda d: d.name
        ):
            print("Using {0} {1}".format(
                dep.name, versions[dep.name].version
            ))
