# fastfiles
File storage (Local, Memory, and Cloud) for fastapi. Proof of concept for [filestore](https://github.com/Ichinga-Samuel/faststore)

```python
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from fastfiles import S3, Local, Memory, FileData

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory='')

s3 = S3(extra_args={'ACL': 'public-read'})
memory = Memory()
local = Local()

@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})

# Upload to s3. For single file upload we assume the file input element name is file
@app.post('/s3_upload', name='s3_upload')
async def upload(file: FileData = Depends(s3)) -> FileData:
    return file

# Upload to local disk. For multiple file upload we assume the file input element name is files.
@app.post('/local_upload', name='local_upload')
async def upload(files: list[FileData] = Depends(local)) -> list[FileData]:
    return files

# Upload to memory.
@app.post('/memory_upload', name='memory_upload')
async def upload(file: FileData = Depends(memory)) -> FileData:
    return file
```

## S3 Usage
To  use s3 make sure the following environment variables are set
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- AWS_BUCKET_NAME

