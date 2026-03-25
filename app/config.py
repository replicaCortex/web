import os

DB_USER = os.getenv("DB_USER", "student")
DB_PASSWORD = os.getenv("DB_PASSWORD", "student_secure_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wp_labs")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "access_secret")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "refresh_secret")
JWT_ACCESS_EXPIRATION = int(os.getenv("JWT_ACCESS_EXPIRATION", "15"))  # минуты
JWT_REFRESH_EXPIRATION = int(
    os.getenv("JWT_REFRESH_EXPIRATION", "10080")
)  # минуты (7 дней)

YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID", "")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET", "")
YANDEX_CALLBACK_URL = os.getenv(
    "YANDEX_CALLBACK_URL", "http://localhost:4200/auth/oauth/yandex/callback"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
