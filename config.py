from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")
GITHUB_REPO=os.getenv("Github_Repo")
# Optional: Raise an error if variables are missing
if not GITHUB_TOKEN or not DROPBOX_ACCESS_TOKEN:
    raise ValueError("Required environment variables are missing!")
