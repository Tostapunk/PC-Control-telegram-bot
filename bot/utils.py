import os


def current_path() -> str:
    return os.path.abspath(os.path.dirname(__file__))  
