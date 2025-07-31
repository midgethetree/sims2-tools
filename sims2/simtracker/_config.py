from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import confighome


# TODO: make paths configurable via ui
def save_config() -> None:
    """Save config file."""
    with _path.open("w", encoding="utf-8") as file:
        config.write(file)


def _load_config() -> None:
    if _path.exists():
        config.read(_path)
        return

    config["paths"]["1"] = str(
        Path.home()
        / "Documents/EA Games/The Sims™ 2 Ultimate Collection/Neighborhoods",
    )

    save_config()


_path: Path = confighome / "simtracker/config.ini"
_path.parent.mkdir(parents=True, exist_ok=True)
config: ConfigParser = ConfigParser()
config.read(Path(__file__).parent / "config.ini")
_load_config()

folders_nhoods: list[Path] = [Path(x) for x in config["paths"].values()]
config_traits: bool = config.getboolean("config", "traits")
