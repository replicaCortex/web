import os


class Settings:
    DB_USER: str = os.getenv("DB_USER", "student")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "student_secure_password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "wp_labs")
    APP_PORT: int = int(os.getenv("APP_PORT", "4200"))

    @property
    def DATABASE_URL(self) -> str:
        if os.getenv("USE_SQLITE", "1") == "1":
            return "sqlite+aiosqlite:///./app.db"
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    DB_ECHO: bool = False
    APP_TITLE: str = "FooBar API"


settings = Settings()
