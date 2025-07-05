import os
import requests
import logging
from typing import Optional, List, Dict


class CloudStorage:
    def __init__(self, token: str, backup_folder: str):
        self.token = token
        self.backup_folder = backup_folder.strip("/")
        self.api_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def _get_remote_path(self, relative_path: str) -> str:
        return f"{self.backup_folder}/{relative_path}".replace("\\", "/")

    def create_folder(self) -> bool:
        params = {"path": self.backup_folder}
        try:
            response = requests.put(self.api_url, headers=self.headers, params=params)
            if response.status_code == 201:
                logging.info(f"Папка '{self.backup_folder}' успешно создана на Яндекс.Диске")
                return True
            elif response.status_code == 409:
                logging.info(f"Папка '{self.backup_folder}' уже существует на Яндекс.Диске")
                return True
            else:
                logging.error(f"Ошибка создания папки '{self.backup_folder}': {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"Исключение при создании папки '{self.backup_folder}': {e}")
        return False

    def _get_upload_url(self, remote_path: str, overwrite: bool = False) -> Optional[str]:
        params = {"path": remote_path, "overwrite": "true" if overwrite else "false"}
        try:
            response = requests.get(f"{self.api_url}/upload", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("href")
        except requests.RequestException as e:
            logging.error(f"Ошибка получения URL для загрузки файла '{remote_path}': {e}")
        return None

    def load(self, local_path: str, relative_path: str) -> bool:
        remote_path = self._get_remote_path(relative_path)
        upload_url = self._get_upload_url(remote_path, overwrite=False)
        if not upload_url:
            return False
        try:
            with open(local_path, "rb") as file:
                response = requests.put(upload_url, data=file)
            if response.status_code in (201, 202):
                logging.info(f"Файл '{relative_path}' загружен на Яндекс.Диск.")
                return True
            logging.error(f"Ошибка загрузки файла '{relative_path}': {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"Исключение при загрузке файла '{relative_path}': {e}")
        return False

    def reload(self, local_path: str, relative_path: str) -> bool:
        remote_path = self._get_remote_path(relative_path)
        upload_url = self._get_upload_url(remote_path, overwrite=True)
        if not upload_url:
            return False
        try:
            with open(local_path, "rb") as file:
                response = requests.put(upload_url, data=file)
            if response.status_code in (201, 202):
                logging.info(f"Файл '{relative_path}' обновлен на Яндекс.Диске.")
                return True
            logging.error(f"Ошибка обновления файла '{relative_path}': {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"Исключение при обновлении файла '{relative_path}': {e}")
        return False

    def delete(self, relative_path: str) -> bool:
        remote_path = self._get_remote_path(relative_path)
        params = {"path": remote_path}
        try:
            response = requests.delete(self.api_url, headers=self.headers, params=params)
            if response.status_code == 204:
                logging.info(f"Файл '{relative_path}' удален с Яндекс.Диска.")
                return True
            logging.error(f"Ошибка удаления файла '{relative_path}': {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"Исключение при удалении файла '{relative_path}': {e}")
        return False

    def get_info(self) -> List[Dict]:
        params = {"path": self.backup_folder, "limit": 1000}
        try:
            response = requests.get(self.api_url, headers=self.headers, params=params)
            response.raise_for_status()
            json_data = response.json()
            return json_data.get("embedded", {}).get("items", [])
        except requests.RequestException as e:
            logging.error(f"Ошибка получения информации с Яндекс.Диска: {e}")
            return []
