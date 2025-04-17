from googleapiclient.http import MediaFileUpload
from pathlib import Path

from googleapiclient.discovery import build
from google.oauth2 import service_account
import mimetypes

creds = service_account.Credentials.from_service_account_file(
    'google_key.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

drive_service = build('drive', 'v3', credentials=creds)


def upload_file_to_drive(file_path: str,
                         file_name: str,
                         folder_id: str = '18EEp2MBw9ClfZ8fSEdI72ekl2BnYFQMO'):

    query = (
        f"name='{file_name}' and "
        f"'{folder_id}' in parents and trashed = false"
    )

    response = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    files = response.get("files", [])
    mime_type, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mime_type or 'application/octet-stream')

    if files:
        file_id = files[0]["id"]
        updated_file = drive_service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True
        ).execute()
        return updated_file.get("id")
    else:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        created_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()

    return created_file.get("id")
