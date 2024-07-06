from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import confighome


# TODO: make paths configurable via ui
def _load_config() -> None:
    path: Path = Path(confighome) / "simtracker/config.ini"

    if path.exists():
        config.read(path)
        return

    config["paths"]["1"] = str(
        Path.home()
        / "Documents/EA Games/The Sims™ 2 Ultimate Collection/Neighborhoods",
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w+", encoding="utf-8") as file:
        config.write(file)


config: ConfigParser = ConfigParser()
config.read(Path(__file__).parent / "config.ini")
_load_config()

folders_nhoods: list[Path] = [Path(x) for x in config["paths"].values()]
config_traits: bool = config.getboolean("config", "traits")
