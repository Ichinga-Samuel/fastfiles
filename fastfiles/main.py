from abc import ABC, abstractmethod
from logging import getlogger 

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl

logger = getlogger(__main__)


class FileData(BaseModel):
    """
    Represents the result of an upload operation
    Attributes:
        url (HttpUrl | str): A URL for accessing the object.
        status (bool): True if the upload is successful else False.
        error_message (str): Error message for failed upload.
    """
    url: HttpUrl | str = ""
    status: bool = False
    error_message: str = ""


class CloudUpload(ABC):
    """
    Methods:
        upload: Uploads a single object to the cloud
        multi_upload: Upload multiple objects to the cloud

    Attributes:
        A single FileData object for a single upload and a list of FileData objects for multiple uploads.
    """

    def __init__(self, config: dict | None = None):
        """"
        Keyword Args:
            config (dict): A dictionary of config settings
        """"
        self.result: FileData | list[FileData] = FileData()
        self.config = config or {}
        
    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileData | list[FileData]:
        try:
            if file:
                return await self.upload(file)
    
            elif files:
                return await self.multi_upload(files=files)
        except Exception as err:
            return FileData(status=False, error_message=str(err))

    @abstractmethod
    async def upload(self, *, file: UploadFile | None = None) -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """"""
