from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Define GitHub API configurations
GITHUB_REPO = "<your-github-username>/<your-repo-name>"  # Replace with your GitHub repo
GITHUB_TOKEN = "<your-github-token>"  # Replace with your GitHub Personal Access Token
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

class AppSigningRequest(BaseModel):
    p12_url: str
    mobileprovision_url: str
    p12_password: str
    ipa_url: str
    app_name: str
    bundle_id: str

@app.post("/sign-app/")
async def sign_app(
    p12_url: str = Form(...),
    mobileprovision_url: str = Form(...),
    p12_password: str = Form(...),
    ipa_url: str = Form(...),
    app_name: str = Form(...),
    bundle_id: str = Form(...)
):
    """
    API Endpoint to trigger app signing via GitHub Actions
    """
    # Prepare payload for GitHub Actions
    payload = {
        "event_type": "sign-app",
        "client_payload": {
            "p12_url": p12_url,
            "mobileprovision_url": mobileprovision_url,
            "p12_password": p12_password,
            "ipa_url": ipa_url,
            "app_name": app_name,
            "bundle_id": bundle_id,
        },
    }

    # Trigger GitHub Actions workflow
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.post(GITHUB_DISPATCH_URL, headers=headers, json=payload)

    if response.status_code == 204:
        return {
            "message": "App signing request has been successfully triggered. Please check your email or return for updates.",
            "status": "success",
        }
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@app.get("/")
async def root():
    return {"message": "iOS App Signing Backend is Running!"}
