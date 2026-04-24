import os

JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "access_secret")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "refresh_secret")
JWT_ACCESS_EXPIRATION = int(os.getenv("JWT_ACCESS_EXPIRATION", "15"))
JWT_REFRESH_EXPIRATION = int(os.getenv("JWT_REFRESH_EXPIRATION", "10080"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "my_super_secret_password")
CACHE_TTL = int(os.getenv("CACHE_TTL_DEFAULT", "300"))

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://student:student_secure_password@mongo:27017/wp_labs?authSource=admin",
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID", "")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET", "")
YANDEX_CALLBACK_URL = os.getenv(
    "YANDEX_CALLBACK_URL", "http://localhost:4200/auth/oauth/yandex/callback"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
