from fastapi import FastAPI, Form, UploadFile, File, HTTPException
import requests
from io import BytesIO

app = FastAPI()

# GitHub API configurations
GITHUB_REPO = "alialamidie/P12Website"  # Replace with your GitHub repo
  # Replace with your GitHub Personal Access Token
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

@app.post("/sign-app/")
async def sign_app(
    p12File: UploadFile = File(...),
    mobileProvision: UploadFile = File(...),
    password: str = Form(...),
    ipaFile: UploadFile = File(...),
    appName: str = Form(...),
    bundleId: str = Form(...)
):
    """
    API Endpoint to trigger app signing via GitHub Actions
    """
    # Save the files temporarily
    p12_url = await save_file(p12File)
    mobileprovision_url = await save_file(mobileProvision)
    ipa_url = await save_file(ipaFile)
    
    # Prepare payload for GitHub Actions
    payload = {
        "event_type": "sign-app",
        "client_payload": {
            "p12_url": p12_url,
            "mobileprovision_url": mobileprovision_url,
            "p12_password": password,
            "ipa_url": ipa_url,
            "app_name": appName,
            "bundle_id": bundleId,
        },
    }

    # Trigger GitHub Actions workflow
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.post(GITHUB_DISPATCH_URL, headers=headers, json=payload)

    if response.status_code == 204:
        return {"message": "App signing request successfully triggered.", "status": "success", "download_link": "signed_ipa_url"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

async def save_file(file: UploadFile):
    """
    Helper function to save a file temporarily and return its URL or path.
    """
    # You can modify this to save files on a server or cloud storage.
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

@app.get("/")
async def root():
    return {"message": "iOS App Signing Backend is Running!"}
