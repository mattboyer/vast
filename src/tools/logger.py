import _curses
import blessings
import logging
import sys

app_pkg_name = __name__.split('.')[0]
try:
    term = blessings.Terminal()
except _curses.error as terminal_error:
    class FakeTerm(object):
        def __getattr__(self, term_attr):
            return ''
    term = FakeTerm()


class FormattingStringHandler(logging.StreamHandler):
    '''
    Behaves like :class:`~logging.StreamHandler` (i.e. immediately writes
    messages to the target stream which is sys.stderr by default), but adds
    some formatting to the messages to make them look prettier.
    '''

    level_colours = {
        'WARNING': term.yellow,
        'ERROR': term.red,
        'EXCEPTION': term.red + term.bold,
    }

    def emit(self, record):
        if record.name.startswith(app_pkg_name):
            module_path_formatting = term.bold
        else:
            module_path_formatting = term.black + term.bold
        setattr(record, '_name_format', module_path_formatting)

        try:
            setattr(
                record,
                '_levelname_format',
                FormattingStringHandler.level_colours[record.levelname]
            )
        except KeyError:
            setattr(record, '_levelname_format', '')

        super().emit(record)


console_handler = FormattingStringHandler(stream=sys.stdout)

_app_console_format = ''.join((
    # Formatted log level
    '{_levelname_format}',
    '{levelname:>10}',
    term.normal, '| ',

    # Formatted module path
    '{_name_format}',
    '{name:<30} ',
    term.normal,

    # And finally, the message!
    '-- {message}'
))
console_formatter = logging.Formatter(_app_console_format, style='{')
console_handler.setFormatter(console_formatter)

top_level_logger = logging.getLogger(app_pkg_name)

# When running unit tests, Nose will set a buffering handler defined in its
# 'logcapture' plugin on the root logger. Since we do want Nose to capture
# logs using its own handler and don't want them to be duplicated, we
# choose to skip adding our custom handler whe the root logger already has
# a handler
root_logger = logging.getLogger(None)
if not root_logger.handlers:
    top_level_logger.addHandler(console_handler)


def ModuleLogger(module_qualname):
    return logging.getLogger(module_qualname)


def set_verbosity(level):
    top_level_logger.setLevel(logging.INFO)
    if level > 0:
        top_level_logger.setLevel(logging.DEBUG)
    if level > 1:
        sa_logger = logging.getLogger('sqlalchemy')
        sa_logger.setLevel(logging.INFO)
        sa_logger.addHandler(console_handler)
