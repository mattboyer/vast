from . import Command, CLI_subcmd
from .. import PROJECT_NAME
from ..tools.logger import ModuleLogger

import pip

log = ModuleLogger(__name__)


@CLI_subcmd('version')
class AnalyseCmd(Command):
    '''
    Display version information
    '''

    def run(self, arg_ns):
        versions = {}
        for pkg_metadata in pip.get_installed_distributions():
            versions[pkg_metadata.project_name] = pkg_metadata
        log.info('Running %s %s', PROJECT_NAME, versions[PROJECT_NAME].version)
        for dep in sorted(
            versions[PROJECT_NAME].requires(),
            key=lambda d: d.name
        ):
            log.info('Using %s %s', dep.name, versions[dep.name].version)
