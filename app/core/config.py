import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "HRMS 0.1")
    ENV: str = os.getenv("ENV", "local")  # local/dev/prod
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")

    MONGO_URI: str | None = os.getenv("MONGO_URI")
    MONGO_DB: str = os.getenv("MONGO_DB", "hrms")

    REQUEST_TIMEOUT_MS: int = int(os.getenv("REQUEST_TIMEOUT_MS", "10000"))

    def validate(self) -> None:
        if not self.MONGO_URI:
            raise RuntimeError("MONGO_URI is not set (put it in .env)")

settings = Settings()
