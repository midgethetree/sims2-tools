from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import confighome


def save_config() -> None:
    """Save config file."""
    with _path.open("w", encoding="utf-8") as file:
        config.write(file)


def _load_config() -> None:
    if _path.exists():
        config.read(_path)
        return

    config.read_dict(
        {
            "paths": {
                "downloads": str(
                    Path.home()
                    / "Documents/EA Games/The Sims™ 2 Ultimate Collection/Downloads",
                ),
                "objects": str(
                    Path(
                        "C:/Program Files (x86)/Origin Games/The Sims 2 Ultimate Collection/Fun with Pets/SP9/TSData/Res/Objects/objects.package",
                    ),
                ),
            },
        },
    )

    save_config()


_path: Path = confighome / "simidge/config.ini"
_path.parent.mkdir(parents=True, exist_ok=True)
config: ConfigParser = ConfigParser()
_load_config()
