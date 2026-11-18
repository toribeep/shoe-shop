import configparser
import sys
from pathlib import Path

def get_config_path():
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / "config.ini"


config = configparser.ConfigParser()
config_path = get_config_path()

if not config_path.exists():
    raise FileNotFoundError(
        f"Файл настроек не найден: {config_path}"
    )

config.read(config_path, encoding="utf-8")

DB_CONFIG = {
    "host": config["postgresql"]["host"],
    "database": config["postgresql"]["database"],
    "user": config["postgresql"]["user"],
    "password": config["postgresql"]["password"],
    "port": config.getint("postgresql", "port")
}