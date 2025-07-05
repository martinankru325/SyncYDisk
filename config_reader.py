import os
import configparser


def read_config(config_path: str) -> dict:
    config = configparser.ConfigParser()
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Файл конфигурации '{config_path}' не найден.")
    config.read(config_path)

    try:
        local_folder = config.get("Settings", "local_folder")
        cloud_folder = config.get("Settings", "cloud_folder")
        token = config.get("Settings", "token")
        sync_interval = config.getint("Settings", "sync_interval")
        log_file = config.get("Settings", "log_file")
    except Exception as e:
        raise ValueError(f"Ошибка чтения параметров из config.ini: {e}")

    if not os.path.isdir(local_folder):
        raise FileNotFoundError(f"Локальная папка '{local_folder}' не существует.\nПроверьте параметр local_folder в config.ini.")
    if not token or token.strip() == "":
        raise ValueError("Токен доступа не задан или пуст.\nПроверьте параметр token в config.ini.")

    return {
        "local_folder": local_folder,
        "cloud_folder": cloud_folder,
        "token": token,
        "sync_interval": sync_interval,
        "log_file": log_file,
    }
