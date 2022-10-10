import asyncio
import logging
import os

from azure.storage.blob import BlobServiceClient

from .main import CloudUpload, FileData, UploadFile

logger = logging.getLogger(__name__)


class AzureStorage(CloudUpload):
    def __init__(self, *, file: bytes | UploadFile or None = None, files: list[UploadFile | bytes] or None = None,
                 connection_string: str = "", container_name: str = "", credential=None, **kwargs):
        super().__init__(file=file, files=files, **kwargs)
        self.connection_str = connection_string or os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = container_name or os.environ['CONTAINER_NAME']
        self.credential = credential

    async def get_client(self):
        return await asyncio.to_thread(BlobServiceClient.from_connection_string, conn_str=self.connection_str, credential=self.credential)

    async def upload(self, name: str = ""):
        """"""
        name = name or self.name
        file_data = await self._upload_file(file=self.file, name=name)
        self.response = file_data

    async def _upload_file(self, *, file, name: str = "", client=None) -> FileData:
        try:
            client = client or await self.get_client()
            blob_name = name or file.filename
            blob_client = client.get_blob_client(container=self.container_name, blob=blob_name)
            await asyncio.to_thread(blob_client.upload_blob, file.file)
            return FileData(public_url=blob_client.url)
        except Exception as err:
            logger.error(err)
            return FileData(status=False)

    async def multi_upload(self, *args, **kwargs):
        client = await self.get_client()
        tasks = [asyncio.create_task(self._upload_file(file=file, client=client)) for file in self.files]
        self.response = await asyncio.gather(*tasks)
