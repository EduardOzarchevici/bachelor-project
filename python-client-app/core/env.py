from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_DEFAULT_API_BASE_URL = "http://localhost:8081/api"


def get_api_base_url() -> str:
    """Read API_BASE_URL from .env on every call."""
    value = _read_env_value("API_BASE_URL")
    return value if value else _DEFAULT_API_BASE_URL


def _read_env_value(key: str) -> str | None:
    if not _ENV_PATH.exists():
        return None

    with open(_ENV_PATH, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            env_key, env_value = line.split("=", 1)
            if env_key.strip() == key:
                return env_value.strip().strip('"').strip("'")
    return None
