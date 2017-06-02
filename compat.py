## @package PyHoot.compat
# Getting the OS ready
## @file compat.py Implementation of @ref PyHoot.compat

import os


def __init__():
    """initialization"""
    if not getattr(os, 'O_BINARY'):
        os.O_BINARY = 0
