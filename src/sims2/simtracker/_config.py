from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import get_path, load, save


# TODO: make paths configurable via ui
def save_config() -> None:
    """Save config file."""
    save(config, _path)


_path: Path = get_path("simtracker")
config: ConfigParser = load(
    _path,
    {
        "paths": {
            "1": str(
                Path.home()
                / "Documents/EA Games/The Sims™ 2 Ultimate Collection/Neighborhoods",
            ),
        },
    },
    default_file=Path(__file__).parent / "config.ini",
)

folders_nhoods: list[Path] = [Path(x) for x in config["paths"].values()]
config_traits: bool = config.getboolean("config", "traits")
