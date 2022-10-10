import os
import asyncio
import logging
from urllib.parse import quote as urlencode

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .main import CloudUpload, FileData, UploadFile

logger = logging.getLogger(__name__)


class S3(CloudUpload):
    def __init__(self, *, file: bytes | UploadFile or None = None, files: list[UploadFile | bytes] or None = None, region_name: str = "",
                 aws_access_key_id: str = "", aws_secret_access_key: str = "",
                 bucket_name: str = "", **kwargs):
        super().__init__(file=file, files=files, **kwargs)
        self.region_name = region_name or os.environ.get('AWS_REGION')
        self.aws_access_key_id = aws_access_key_id or os.environ.get('AWS_ACCESS_KEY')
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get('AWS_SECRET_KEY')
        self.bucket_name = bucket_name or os.environ['S3_BUCKET_NAME']

    async def get_client(self):
        return await asyncio.to_thread(boto3.client, 's3', region_name=self.region_name, aws_access_key_id=self.aws_access_key_id,
                                       aws_secret_access_key=self.aws_secret_access_key)

    async def upload(self, name: str = ""):
        """"""
        name = name or self.name
        file_data = await self._upload_file(file=self.file, name=name)
        self.response = file_data

    async def _upload_file(self, *, file, name: str = "", client=None) -> FileData:
        try:
            s3 = client or await self.get_client()
            object_name = name or file.filename
            file = file.file
            await asyncio.to_thread(s3.upload_fileobj, file, self.bucket_name, object_name, ExtraArgs=self.extra_args)
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{urlencode(object_name.encode('utf8'))}"
            return FileData(public_url=url)
        except (NoCredentialsError, ClientError, Exception) as err:
            logger.error(err)
            return FileData(status=False)

    async def multi_upload(self, *args, **kwargs):
        client = await self.get_client()
        tasks = [asyncio.create_task(self._upload_file(file=file, client=client)) for file in self.files]
        self.response = await asyncio.gather(*tasks)
