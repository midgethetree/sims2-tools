"""Common utilities shared between SiMidge and SimTracker for handling configuration."""

import os
from pathlib import Path

if "APPDATA" in os.environ:
    confighome: Path = Path(os.environ["APPDATA"])
elif "XDG_CONFIG_HOME" in os.environ:
    confighome = Path(os.environ["XDG_CONFIG_HOME"])
else:
    confighome = Path(os.environ["HOME"]) / ".config"
