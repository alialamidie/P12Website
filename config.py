from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access environment variables
GITHUB_TOKEN = os.getenv("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")
DROPBOX_ACCESS_TOKEN = os.getenv("sl.CDNXZADIpLmXHG4CzsFgvpp9P6ZetbncqBZk4dq5IAHQqlLwmXHrt-Xxsu1CXpYGLodU0tjtsQ_6i49AWgBkR5AjeGgJ8DnQbmW2Etu4ZuGWBXc-zzKpjuXKEZ0gswTelUJWpPYMxw9ZZ31Kb2hPFK0")

# Optional: Raise an error if variables are missing
if not GITHUB_TOKEN or not DROPBOX_ACCESS_TOKEN:
    raise ValueError("Required environment variables are missing!")
