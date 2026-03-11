class Settings:
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    DB_ECHO: bool = False
    APP_TITLE: str = "FooBar"


settings = Settings()
