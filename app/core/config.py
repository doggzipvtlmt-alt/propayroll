import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Doggzi Office OS")
    ENV: str = os.getenv("ENV", "local")  # local/dev/prod
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")

    MONGO_URI: str | None = os.getenv(
        "MONGO_URI",
        "mongodb+srv://doggzipvtlmt_db_user:Uunitech123@cluster0.wpzevmb.mongodb.net/?appName=Cluster0",
    )
    MONGO_DB: str = os.getenv("MONGO_DB", "doggzi_office_os")
    MONGO_STARTUP_STRICT: bool = os.getenv("MONGO_STARTUP_STRICT", "true").lower() == "true"

    REQUEST_TIMEOUT_MS: int = int(os.getenv("REQUEST_TIMEOUT_MS", "10000"))

    def validate(self) -> None:
        if not self.MONGO_URI:
            raise RuntimeError("MONGO_URI is not set (put it in .env)")

settings = Settings()
