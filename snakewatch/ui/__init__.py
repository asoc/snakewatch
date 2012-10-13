import sys

from . import Console, Qt

def get_handler(console):
    if not console:
        try:
            import PySide
        except ImportError:
            print sys.stderr, 'Unable to load PySide library. Please ensure' \
                              ' it is installed and on your PYTHONPATH or ' \
                              ' run in console mode.'
            sys.exit(1)
        
        return Qt.QtHandler()
        
    return Console.ConsoleHandler()
