from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import get_path, load, save


def save_config() -> None:
    """Save config file."""
    save(config, _path)


_path: Path = get_path("simidge")
config: ConfigParser = load(
    _path,
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
