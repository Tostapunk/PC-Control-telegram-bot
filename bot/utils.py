import os


def current_path():
    return os.path.dirname(os.path.abspath(__file__))[:-4]
