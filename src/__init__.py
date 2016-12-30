import os.path
import xdg.BaseDirectory
from pkg_resources import safe_name, to_filename

# Vast Address-space Surveying Tool
PROJECT_NAME = 'vast'
PROJECT_NAME = to_filename(safe_name(PROJECT_NAME))

PROJECT_DESCRIPTION = 'lorem ipsum'

# TODO Take the env into account and/or a conf file
SQLITE_PATH = os.path.join(
    xdg.BaseDirectory.save_data_path(PROJECT_NAME),
    PROJECT_NAME + '.sqlite'
)
