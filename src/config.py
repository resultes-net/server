import os as _os

DB_HOST_NAME = _os.environ.get("DB_HOST_NAME")
if not DB_HOST_NAME:
    import socket

    host_name = socket.gethostname()
    # Can't access Windows' `localhost` using "localhost".
    # Cf.:https://superuser.com/questions/1679757/accessing-windows-localhost-from-wsl2
    DB_HOST_NAME = f"{host_name}.local"
    print(f"Accessing Windows localhost via '{DB_HOST_NAME}'.")

DB_PORT = _os.environ.get("DB_PORT", "8432")

DB_CONNECTION_STRING = (
    f"postgresql+psycopg://postgres:postgres@{DB_HOST_NAME}:{DB_PORT}/resultes"
)

ROOT_PATH = _os.environ.get("ROOT_PATH", "")
