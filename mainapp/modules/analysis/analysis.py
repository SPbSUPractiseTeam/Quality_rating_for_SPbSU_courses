from .video import main as video_analysis
from .tests import main as tests_analysis
import sqlite3

_modules = {'video': video_analysis, 'tests': tests_analysis}

_database = None
_cursor = None
_course_name = None
_path = None


def set_data(database_name, path):
    global _cursor, _database, _course_name, _path
    _database = sqlite3.connect(database_name)
    _course_name = database_name.split('.')[0]
    _cursor = _database.cursor()
    _path = path


def use_module(name):
    global _cursor, _course_name, _modules, _path
    if name not in _modules:
        return None
    else:
        return _modules[name].execute(_cursor, _course_name, _path)
