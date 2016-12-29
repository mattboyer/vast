import argparse
from . import COMMAND_REGISTRY, register
from .. import PROJECT_DESCRIPTION
from ..tools.logger import ModuleLogger, set_verbosity

log = ModuleLogger(__name__)


def subcmd_dispatcher(args_ns):
    '''
    Instantiates and runs the command class associated to the subcommand
    invoked on the CLI.
    '''

    try:
        subcmd = args_ns.subcmd
    except AttributeError:
        raise ValueError("No subcommand specified")

    log.debug("Running subcommand '%s' with args %r", subcmd, args_ns)
    subcmd_instance = COMMAND_REGISTRY[subcmd]()
    subcmd_instance.run(args_ns)


def main():
    # Discover(?) and import subcommand modules
    register()

    # We need a separate parser for the verbose flag. This will be a parent
    # parser to both the top-level parser and individual subcommand parsers.
    # See https://code.google.com/archive/p/argparse/issues/54
    verbose_parser = argparse.ArgumentParser(add_help=False)
    verbose_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='Give more output. Option is additive, and can be used '
        'up to 3 times.',
    )

    cli_parser = argparse.ArgumentParser(
        description=PROJECT_DESCRIPTION,
        parents=[verbose_parser],
    )

    subcmd_parsers = cli_parser.add_subparsers(
        title='Subcommands',
        description='%(prog)s implements the following subcommands:',
        dest='subcmd',
    )

    for sub_cmd in sorted(COMMAND_REGISTRY.keys()):
        subcmd_class = COMMAND_REGISTRY[sub_cmd]
        subcmd_parser = subcmd_parsers.add_parser(
            sub_cmd,
            parents=[verbose_parser],
            help=subcmd_class.get_description(),
            description=subcmd_class.get_description()
        )
        subcmd_class.configure_parser(subcmd_parser)

    cli_args_ns = cli_parser.parse_args()
    verbosity_level = cli_args_ns.verbose or 0
    set_verbosity(verbosity_level)

    if cli_args_ns.subcmd:
        subcmd_dispatcher(cli_args_ns)
    else:
        # No subcommand specified, print the usage and bail
        cli_parser.print_usage()
