import os
import logging
from typing import Dict


def get_local_files_info(folder: str) -> Dict[str, float]:
    """
    Рекурсивно получает словарь {относительный_путь_к_файлу: время_последней_модификации}
    """
    files_info = {}
    try:
        for root, _, files in os.walk(folder):
            for filename in files:
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, folder).replace("\\", "/")
                files_info[relative_path] = os.path.getmtime(full_path)
    except Exception as e:
        logging.error(f"Ошибка при чтении локальных файлов: {e}")
    return files_info


def sync_files(local_folder: str, cloud_storage, prev_files_info: dict) -> dict:
    current_files_info = get_local_files_info(local_folder)

    # Новые и измененные файлы
    for relative_path, mtime in current_files_info.items():
        local_path = os.path.join(local_folder, relative_path)
        if relative_path not in prev_files_info:
            success = cloud_storage.load(local_path, relative_path)
            if success:
                logging.info(f"Новый файл '{relative_path}' загружен в облако.")
            else:
                logging.error(f"Не удалось загрузить новый файл '{relative_path}'.")
        elif mtime != prev_files_info.get(relative_path):
            success = cloud_storage.reload(local_path, relative_path)
            if success:
                logging.info(f"Файл '{relative_path}' обновлен в облако.")
            else:
                logging.error(f"Не удалось обновить файл '{relative_path}'.")

    # Удаленные файлы
    deleted_files = set(prev_files_info.keys()) - set(current_files_info.keys())
    for relative_path in deleted_files:
        success = cloud_storage.delete(relative_path)
        if success:
            logging.info(f"Удаленный файл '{relative_path}' удален из облака.")
        else:
            logging.error(f"Не удалось удалить файл '{relative_path}' из облака.")

    return current_files_info
