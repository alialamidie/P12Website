import dropbox
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
import os
from dropbox.exceptions import ApiError

app = FastAPI()

origins = [
    "https://alialamidie.github.io",  # Allow only this origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# GitHub API configurations
GITHUB_REPO = "alialamidie/P12Website"
GITHUB_TOKEN = "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"
GITHUB_DISPATCH_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

# Dropbox API configurations
DROPBOX_ACCESS_TOKEN = "sl.CDPlYjcxeHAu4yvR66GYkNcRtkwSAoUIFwrnSlUlhMRmziSf8Lg_NoAwLnF2kLvc7J-uJQmtUE7J8yPFHWXaCIbb8DWt6_VvLQwYxpOgisQwfww5FBPnLVeBJAC5_WcGVB_A1cfI9rud2p4VPDhH2eU"
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
        # Upload the signed IPA file to Dropbox
        signed_ipa_url = await upload_to_dropbox(ipa_url)
        return {"message": "App signing request successfully triggered.", "status": "success", "download_link": signed_ipa_url}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


async def save_file(file: UploadFile):
    """
    Helper function to save a file temporarily and return its path.
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())  # Corrected for async file reading
    
    return file_path


async def upload_to_dropbox(file_path: str) -> str:
    """
    Upload a file to Dropbox and return a shareable link.
    """
    with open(file_path, "rb") as f:
        file_content = f.read()

    dropbox_path = f"/{os.path.basename(file_path)}"

    try:
        # Upload file to Dropbox
        dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode.overwrite)

        # Check for existing shared link or create a new one
        shared_links = dbx.sharing_list_shared_links(path=dropbox_path)
        if shared_links.links:
            shared_link_metadata = shared_links.links[0]
        else:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)

        # Convert shared link to direct download
        download_link = shared_link_metadata.url.replace('?dl=0', '?dl=1')
        return download_link

    except ApiError as e:
        print(f"Dropbox API Error: {e}")
        raise HTTPException(status_code=500, detail="Error handling file upload or shared link creation.")

@app.get("/")
async def root():
    return {"message": "iOS App Signing Backend is Running!"}
