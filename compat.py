import os


def __init__():
    if not getattr(os, 'O_BINARY'):
        os.O_BINARY = 0
