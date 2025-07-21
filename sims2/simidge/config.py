from configparser import ConfigParser
from pathlib import Path

from sims2.common.config import confighome


# TODO: make paths configurable via ui
def _load_config() -> None:
    path: Path = confighome / "simidge/config.ini"

    if path.exists():
        config.read(path)
        return

    config["paths"] = {}
    config["paths"]["downloads"] = str(
        Path.home() / "Documents/EA Games/The Sims™ 2 Ultimate Collection/Downloads",
    )
    config["paths"]["objects"] = str(
        Path(
            "C:/Program Files (x86)/Origin Games/The Sims 2 Ultimate Collection/Fun with Pets/SP9/TSData/Res/Objects/objects.package",
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        config.write(file)


config: ConfigParser = ConfigParser()
_load_config()
