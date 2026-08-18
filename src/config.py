import os as _os

DB_HOST_NAME = _os.environ.get("DB_HOST_NAME", "localhost")

# To connect to the DB in the Kubernetes cluster, set to 6432 and forward from within WSL like so
#   `kubectl port-forward -n server service/server-db 6432:5432`.
# If, for some reason, you want to forwad from within Windows, make sure to listen on an IP address
# that WSL can access, e.g.
#   `kubectl port-forward --address=172.20.64.1 -n server service/server-db 6432:5432`
# You'll also need to add a firewall rule to allow connections to 172.20.61.1:6432 from, e.g.,
# 172.20.0.0/16.
DB_PORT = _os.environ.get("DB_PORT", "5432")
DB_USER = _os.environ.get("DB_USER", "postgres")
DB_PASSOWRD = _os.environ.get("DB_PASSWORD", "postgres")

DB_CONNECTION_STRING = (
    f"postgresql+psycopg://{DB_USER}:'{DB_PASSOWRD}'@{DB_HOST_NAME}:{DB_PORT}/resultes"
)

ROOT_PATH = _os.environ.get("ROOT_PATH", "")

RESULTES_RESULTS_CONTAINER = "resultes-results"
