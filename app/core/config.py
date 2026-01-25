import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "hrms")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set")
