"""Common utilities shared between SiMidge and SimTracker for handling configuration."""

import os
from os import environ
from pathlib import Path

if "APPDATA" in environ:
    confighome: Path = Path(environ["APPDATA"])
elif "XDG_CONFIG_HOME" in os.environ:
    confighome = Path(environ["XDG_CONFIG_HOME"])
else:
    confighome = Path(environ["HOME"]) / ".config"
