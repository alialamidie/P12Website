import dropbox
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
import requests
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import os
app = FastAPI()

origins = [
    "https://alialamidie.github.io",  # Allow only this origin
    # You can add other domains here if needed
]

# Allow CORS for your frontend (replace "*" with the specific domain of your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://alialamidie.github.io"],  # Allow only this origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# GitHub API configurations
GITHUB_REPO = "alialamidie/P12Website"  # Replace with your GitHub repo
GITHUB_TOKEN = "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"  # Replace with your GitHub Personal Access Token
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

# Dropbox API configurations
DROPBOX_ACCESS_TOKEN = "sl.CDO6KKTILW6nyfXan1vCRQO5Oh0dzZFsHBknrzeFQhIt9U7wlDsSoZvWu9PRR8JYxX9ro2ySIsFFGu9svzHfdqdcG_d4ttyX0y6YwpoHh-APt_AlhpSvxNNIV29r5LPR1ZqjArPEt3b5"  # Replace with your Dropbox access token
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

@app.post("/sign-app/")
async def sign_app(
    p12File: UploadFile = File(...),
    mobileProvision: UploadFile = File(...),
    password: str = Form(...),
    ipaFile: UploadFile = File(...),
    appName: str = Form(...),
    bundleId: str = Form(...),
):
    """
    API Endpoint to trigger app signing via GitHub Actions and upload to Dropbox.
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
        # Upload the IPA file to Dropbox after signing
        signed_ipa_url = await upload_to_dropbox("signed_app.ipa")

        return {"message": "App signing request successfully triggered.", "status": "success", "download_link": signed_ipa_url}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

async def save_file(file: UploadFile):
    """
    Helper function to save a file temporarily and return its URL or path.
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)  # Create the 'temp' directory if it doesn't exist

    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return file_path
async def upload_to_dropbox(file_path: str) -> str:
    """
    Upload a file to Dropbox and return the shareable link.
    """
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Upload file to Dropbox
    dropbox_path = f"/{file_path}"  # The path in Dropbox
    dbx.files_upload(file_content, dropbox_path, mute=True)

    # Create a shared link for the uploaded file
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)

    # Extract the link to the file
    download_link = shared_link_metadata.url.replace('?dl=0', '?dl=1')  # Ensure it's a direct download link
    
    return download_link

@app.get("/")
async def root():
    return {"message": "iOS App Signing Backend is Running!"}
