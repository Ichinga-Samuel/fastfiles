from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl

logger = getLogger(__name__)


class FileData(BaseModel):
    """
    Represents the result of an upload operation

    Attributes:
        file (Bytes): File saved to memory
        path (Path | str): Path to file in local storage
        url (HttpUrl | str): A URL for accessing the object.
        size (int): Size of the file in bytes.
        filename (str): Name of the file.
        status (bool): True if the upload is successful else False.
        error (str): Error message for failed upload.
        message: Response Message
    """
    file: bytes = b''
    path: Path | str = ''
    url: HttpUrl | str = ''
    size: int = 0
    filename: str = ''
    content_type: str = ''
    status: bool = True
    error: str = ''
    message: str = ''


class FileUpload(ABC):
    """
    Methods:
        upload: Uploads a single object to the cloud
        multi_upload: Upload multiple objects to the cloud

    Attributes:
        config: A config dict
    """

    def __init__(self, config: dict | None = None):
        """
        Keyword Args:
            config (dict): A dictionary of config settings
        """
        self.config = config or {}
        
    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileData | list[FileData]:
        try:
            if file:
                return await self.upload(file=file)
    
            elif files:
                return await self.multi_upload(files=files)
            else:
                return FileData(status=False, error='No file or files provided', message='No file or files provided')
        except Exception as err:
            return FileData(status=False, error=str(err), message='File upload was unsuccessful')

    @abstractmethod
    async def upload(self, *, file: UploadFile) -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """"""
