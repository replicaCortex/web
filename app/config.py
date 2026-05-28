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


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio_admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_secure_password_change_in_prod")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "wp-labs-files")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "student")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "student_secure_rabbit_pass_change_in_prod")
QUEUE_USER_REGISTERED = os.getenv("QUEUE_USER_REGISTERED", "wp.auth.user.registered")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_SECURE = os.getenv("SMTP_SECURE", "true").lower() == "true"
