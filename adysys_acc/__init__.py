import importlib
import sanic
from sanic_session import Session
import jinja2
import os
from tinydb import TinyDB as tdb
from pathlib import Path
home = os.path.join(Path.home(), 'AdySysAcc')
Path.mkdir(home, parents=True, exist_ok=True)

dbFile = tdb(os.path.join(home, '.adysysacc.qldb'))


