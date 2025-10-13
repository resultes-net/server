import os as _os

DB_HOST_NAME = _os.environ.get("DB_HOST_NAME") or "localhost"

DB_PORT = _os.environ.get("DB_PORT", "5432")

DB_CONNECTION_STRING = (
    f"postgresql+psycopg://postgres:postgres@{DB_HOST_NAME}:{DB_PORT}/resultes"
)

ROOT_PATH = _os.environ.get("ROOT_PATH", "")
