import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)

def upload_avatar(file: UploadFile, public_id: str):
    result = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    return result.get("secure_url")