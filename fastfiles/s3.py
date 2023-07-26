import os
import asyncio
import logging
from urllib.parse import quote as urlencode
from functools import cache

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .main import CloudUpload, FileData, UploadFile

logger = logging.getLogger(__name__)


class S3(CloudUpload)
    @property
    @cache
    def client(self):
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        region_name = os.environ.get('AWS_DEFAULT_REGION') or self.config.get('region')
        return boto3.client('s3', region_name=region_name, aws_access_key_id=key_id, aws_secret_access_key=access_key)

    async def upload(self, *, file: UploadFile) -> FileData:
        try:
            extra_args = self.config.get('extra_args', {})
            bucket = self.config['bucket']
            region = os.environ.get('AWS_DEFAULT_REGION') or self.config.get('region')
            await asyncio.to_thread(self.client.upload_fileobj, file.file, bucket, file.filename, ExtraArgs=extra_args)
            url = f"https://{self.bucket}.s3.{region}.amazonaws.com/{urlencode(file.filename.encode('utf8'))}"
            return FileData(url=url, message=f'{file.filename} uploaded successfully')
        except (NoCredentialsError, ClientError, Exception) as err:
            logger.error(err)
            return FileData(status=False, error=str(err), message='File upload was unsuccessful)

    async def multi_upload(self, *, files: UploadFiles):
        tasks = [asyncio.create_task(self.upload(file=file)) for file in files]
        return await asyncio.gather(*tasks)
