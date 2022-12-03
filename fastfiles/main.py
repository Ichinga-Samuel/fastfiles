from abc import ABC, abstractmethod

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl


class FileData(BaseModel):
    """
    Represents the result of an upload operation
    Attributes:
        public_url (HttpUrl | str): A public url for accessing the object
        status (bool): True or False if upload is successful
    """
    public_url: HttpUrl | str = ""
    status: bool = True


class CloudUpload(ABC):
    """
    Keyword Args:
        file (bytes | UploadFile): File object as bytes or UploadFile object the default value is None
        files (list[bytes | UploadFile]): A list of files for multiple upload
        name (str): A name for the file in the cloud object
        extra_args (dict): A dictionary of optional arguments

    Methods:
        upload: Uploads single object to the cloud
        multi_upload: Upload multiple objects to the cloud

    Attributes:
        response (FileData | list[FileDate]): Response of the file upload operation. A single object for single upload and
        a list for multiple files upload
    """

    def __init__(self, *, file: bytes | UploadFile | None = None, files: list[UploadFile | bytes] | None = None, name: str = "",
                 extra_args: dict | None = None):

        self.file = file
        self.files = files
        self.response: FileData | list[FileData] = FileData()
        self.extra_args = extra_args or {}
        self.name = name

    async def __call__(self, file: bytes | UploadFile | None = None, files: list[UploadFile | bytes] | None = None):
        if file:
            self.file = file
            await self.upload(name=self.name)

        elif files:
            self.files = files
            await self.multi_upload()
        return self

    @abstractmethod
    async def upload(self, name: str = "") -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *args, **kwargs) -> list[FileData]:
        """"""
