from mindsdb.integrations.libs.const import HANDLER_TYPE

from .__about__ import __version__ as version, __description__ as description

try:
    from .empress_handler import (
        EmpressHandler as Handler,
        connection_args_example,
        connection_args
    )

    import_error = None
except Exception as e:
    Handler = None
    import_error = e

title = 'Empress Embedded'
name = 'empress'
type = HANDLER_TYPE.DATA
icon_path = 'icon.png'

__all__ = [
    'Handler', 'version', 'name', 'type', 'title', 'connection_args', 'connection_args_example',
    'description', 'import_error', 'icon_path'
]
