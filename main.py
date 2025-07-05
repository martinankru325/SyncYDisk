import sys
import time
import logging

from config_reader import read_config
from logger_setup import setup_logging
from cloud_storage import CloudStorage
from file_sync import sync_files


def main():
    try:
        config_path = "config.ini"  # путь к вашему файлу конфигурации
        config = read_config(config_path)
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        sys.exit(1)

    setup_logging(config["log_file"])
    logging.info("Запуск службы синхронизации")

    cloud_storage = CloudStorage(token=config["token"], backup_folder=config["cloud_folder"])

    if not cloud_storage.create_folder():
        logging.error("Не удалось создать или получить доступ к папке на Яндекс.Диске. Выход.")
        sys.exit(1)

    previous_files_info = {}

    try:
        while True:
            previous_files_info = sync_files(config["local_folder"], cloud_storage, previous_files_info)
            logging.info(f"Ожидание {config['sync_interval']} секунд до следующей синхронизации.")
            time.sleep(config["sync_interval"])
    except KeyboardInterrupt:
        logging.info("Служба синхронизации остановлена пользователем.")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
