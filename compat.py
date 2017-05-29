"""Setting up os for the program"""

import os


def __init__():
    """initialization"""
    if not getattr(os, 'O_BINARY'):
        os.O_BINARY = 0
