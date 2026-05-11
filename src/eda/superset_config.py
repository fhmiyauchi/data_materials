import os

# ---------------------------------------------------------
# Superset specific config
# All credentials are loaded from environment variables (.env)
# ---------------------------------------------------------

# Secret key for session signing — loaded from SUPERSET_SECRET_KEY in .env
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

# Superset's own metadata DB (dashboards, charts, users etc.)
# Stored in a dedicated named Docker volume, separate from materials.db
SQLALCHEMY_DATABASE_URI = "sqlite:////app/superset_home/superset.db"

# Redis caching
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": "superset-redis",
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 1,
    "CACHE_REDIS_URL": "redis://superset-redis:6379/1",
}
DATA_CACHE_CONFIG = CACHE_CONFIG

# Allow SQLite connections so Superset can query materials.db
# (This is intentionally relaxed for local EDA — do NOT use in production)
PREVENT_UNSAFE_DB_CONNECTIONS = False

# Disable CSRF for local development convenience
WTF_CSRF_ENABLED = False
