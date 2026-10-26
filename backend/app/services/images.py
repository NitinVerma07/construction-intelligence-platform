"""Upload validation for construction-site images."""
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile

from ..config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@dataclass
class ImageInput:
    media_type: str
    data: bytes


def read_image(upload: UploadFile) -> ImageInput:
    if upload.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Unsupported image type. Use JPEG, PNG, WebP or GIF.")
    limit = settings.MAX_IMAGE_MB * 1024 * 1024
    data = upload.file.read(limit + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > limit:
        raise HTTPException(413, f"Image exceeds the {settings.MAX_IMAGE_MB} MB limit.")
    return ImageInput(media_type=upload.content_type, data=data)
