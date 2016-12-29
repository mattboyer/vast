import importlib
import os
import os.path

COMMAND_REGISTRY = {}


def register():
    # TODO Make this dynamic, somehow
    for mod in ('mapper', 'analyse', 'version'):
        importlib.import_module('.' + mod, package=__name__)


def CLI_subcmd(subcmd):
    def register_subcmd_class(subcmd_class):
        COMMAND_REGISTRY[subcmd] = subcmd_class
    return register_subcmd_class


class Command(object):
    '''
    A command that can be triggered from the command line.
    '''

    @classmethod
    def configure_parser(clazz, parser):
        pass

    @classmethod
    def get_description(clazz):
        return clazz.__doc__

    def run(self, arg_ns):
        '''
        arg_ns is an argparse namespace instance!!
        '''
        raise NotImplementedError("Command not implemented!")
