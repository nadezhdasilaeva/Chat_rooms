import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

PASS_ADMIN = os.environ.get("PASS_ADMIN")
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN") 
