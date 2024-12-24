import dropbox
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
import requests
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import os
from dropbox.exceptions import ApiError
app = FastAPI()

origins = [
    "https://alialamidie.github.io",  # Allow only this origin
    # You can add other domains here if needed
]

# Allow CORS for your frontend (replace "*" with the specific domain of your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

# GitHub API configurations
GITHUB_REPO = "alialamidie/P12Website"  # Replace with your GitHub repo
GITHUB_TOKEN = "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"  # Replace with your GitHub Personal Access Token
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

# Dropbox API configurations
DROPBOX_ACCESS_TOKEN = "sl.CDNR6auO2DenU_-tQ9pbBLVwJ3EfgzPePHtKIwGChTWclceokUrZ0VggwcQ7R9oKCeVILZ959DMYzoyPeScykJXdYJyNVZFH4qGVS87Yf64J5cx-nNyLbxxQ6I1LbJgW5PCmNPdTRD0BSFBmb5GJ8Tk"  # Replace with your Dropbox access token
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
        # Upload the signed IPA file to Dropbox after signing
        # Ensure that you pass the correct file name or path of the signed IPA file
        signed_ipa_url = await upload_to_dropbox(ipa_url)  # Change here: pass the correct file path

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
    If a shared link already exists, return the existing link.
    """
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Use the base file name for the Dropbox path
    dropbox_path = f"/{os.path.basename(file_path)}"

    try:
        # Upload file to Dropbox
        dbx.files_upload(file_content, dropbox_path, mute=True)

        try:
            # Try to create or get the existing shared link
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        except ApiError as e:
            # Handle case where shared link already exists
            if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and \
               e.error.is_shared_link_already_exists():
                # Extract shared link metadata from the error object
                shared_link_metadata = e.error.shared_link_already_exists
            else:
                # For other API errors, raise them
                raise e

        # Check if the metadata contains the URL and modify for direct download
        if hasattr(shared_link_metadata, 'url'):
            download_link = shared_link_metadata.url.replace('?dl=0', '?dl=1')  # Ensure it's a direct download link
            return download_link
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve the download link from Dropbox.")

    except ApiError as e:
        print(f"Error uploading file to Dropbox: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to Dropbox")

@app.get("/")
async def root():
    return {"message": "iOS App Signing Backend is Running!"}
