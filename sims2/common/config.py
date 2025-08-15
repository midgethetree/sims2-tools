"""Common utilities shared between SiMidge and SimTracker for handling configuration."""

import os
from configparser import ConfigParser
from pathlib import Path


def save(config: ConfigParser, path: Path) -> None:
    """Save config file.

    Args:
        config: ConfigParser containing config values to save.
        path: File to save to.
    """
    with path.open("w", encoding="utf-8") as file:
        config.write(file)


def load(
    path: Path,
    defaults: dict,
    *,
    default_file: Path | None = None,
) -> ConfigParser:
    """Load config file.

    Args:
        path: File to load from.
        defaults: Dictionary of default config values to use if config file is not found.
        default_file: File with default config values to load before config file.

    Returns:
        ConfigParser with loaded config values.
    """
    config: ConfigParser = ConfigParser()

    if default_file and default_file.exists():
        config.read(default_file)

    if path.exists():
        config.read(path)
        return config

    if isinstance(defaults, Path):
        config.read(defaults)
    else:
        config.read_dict(defaults)

    save(config, path)

    return config


def get_path(appname: str) -> Path:
    """Get path to config file.

    Args:
        appname: Name of tool being run.

    Returns:
        Path to config file.
    """
    if "APPDATA" in os.environ:
        confighome: Path = Path(os.environ["APPDATA"])
    elif "XDG_CONFIG_HOME" in os.environ:
        confighome = Path(os.environ["XDG_CONFIG_HOME"])
    else:
        confighome = Path(os.environ["HOME"]) / ".config"

    path: Path = confighome / appname / "config.ini"
    path.parent.mkdir(parents=True, exist_ok=True)

    return path
