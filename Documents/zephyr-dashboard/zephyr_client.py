import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.zephyrscale.smartbear.com/v2"


class ZephyrScaleClient:
    def __init__(self, api_token: Optional[str] = None):
        token = api_token or os.getenv("ZEPHYR_API_TOKEN")
        if not token:
            raise ValueError("ZEPHYR_API_TOKEN no encontrado. Revisá el archivo .env")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        response.raise_for_status()
        return response.json()

    def get_projects(self) -> list[dict]:
        data = self._get("projects", {"maxResults": 200})
        return data.get("values", [])

    def get_folders(self, project_key: str) -> list[dict]:
        data = self._get("folders", {
            "projectKey": project_key,
            "folderType": "TEST_CASE",
            "maxResults": 1000,
        })
        return data.get("values", [])

    def get_test_cases(self, project_key: str, folder_id: Optional[int] = None) -> list[dict]:
        all_cases = []
        start_at = 0
        max_results = 100

        while True:
            params = {
                "projectKey": project_key,
                "maxResults": max_results,
                "startAt": start_at,
            }
            if folder_id is not None:
                params["folderId"] = folder_id

            data = self._get("testcases", params)
            values = data.get("values", [])
            all_cases.extend(values)

            if data.get("isLast", True) or len(values) < max_results:
                break
            start_at += max_results

        return all_cases
