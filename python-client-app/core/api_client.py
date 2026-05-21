import requests

from core.env import get_api_base_url


class ApiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApiClient, cls).__new__(cls)
            cls._instance.token = None
        return cls._instance

    def set_token(self, token):
        self.token = token

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, endpoint, **kwargs):
        return requests.get(
            f"{get_api_base_url()}{endpoint}",
            headers=self._get_headers(),
            **kwargs,
        )

    def post(self, endpoint, **kwargs):
        return requests.post(
            f"{get_api_base_url()}{endpoint}",
            headers=self._get_headers(),
            **kwargs,
        )

    def put(self, endpoint, **kwargs):
        return requests.put(
            f"{get_api_base_url()}{endpoint}",
            headers=self._get_headers(),
            **kwargs,
        )

    def delete(self, endpoint, **kwargs):
        return requests.delete(
            f"{get_api_base_url()}{endpoint}",
            headers=self._get_headers(),
            **kwargs,
        )
