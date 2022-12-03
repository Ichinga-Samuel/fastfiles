# fastfiles
File upload to the cloud for fastapi\
Sample Usage with Amazon S3

```python
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from fastfiles import S3

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory='templates')
s3 = S3(extra_args={'ACL': 'public-read'})


@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/upload')
async def upload(file: S3 = Depends(s3)):
    print(file.response)
    return RedirectResponse('/', status_code=302)

```
Supports both multiple and single file upload\
For Single upload make sure the file input element name is file. while for multiple files upload it should be named files.
