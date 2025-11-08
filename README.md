# FastAPI `filestore` Demonstration

This project is a FastAPI application that demonstrates various file upload patterns using the `filestore` library.

It serves as a practical guide and runnable example for handling different file upload scenarios, including:

  * Single and multiple file uploads
  * Storage to local disk, Amazon S3, and in-memory
  * Dynamic file naming and destination paths
  * File validation and filtering
  * Using multiple, different storage engines in a single request

For more information on the library itself, see the [faststore (filestore) repository](https://github.com/Ichinga-Samuel/faststore).

-----

## 🚀 Getting Started

Follow these instructions to get the application up and running on your local machine for development and testing.

### 1\. Prerequisites

  * Python 3.11+
  * An Amazon S3 bucket (if you want to test the S3-related endpoints)

### 2\. Installation & Setup

1.  **Save the Code:**
    Save the code you provided as `main.py`.

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Create a file named `requirements.txt` with the following content:

    ```text
    fastapi
    uvicorn[standard]
    filestore
    python-dotenv
    boto3  # Required for S3Engine
    python-multipart
    ```

    Then, install them using pip:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    The application uses a `.env` file to load configuration, especially for S3. Create a file named `.env` in the same directory as `main.py`:

    ```.env
    # --- S3 Configuration ---
    # Your S3 bucket name
    AWS_BUCKET_NAME=your-s3-bucket-name

    # Your AWS credentials (boto3 will also find these if set in your environment)
    AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
    AWS_REGION=your-s3-bucket-region # e.g., us-east-1
    ```

    **Note:** The `filestore` library will automatically pick up these credentials for the `S3Engine`.

### 3\. Running the Application

With your virtual environment active and `.env` file in place, run the application:

```bash
python main.py
```

You should see output from `uvicorn` indicating the server is running, typically on `http://0.0.0.0:8000`.

-----

## 📂 Project Structure

This project consists of a single file, but it creates directories upon first use:

```
.
├── .env                 # Your environment variables
├── main.py              # The main FastAPI application
├── requirements.txt     # Python dependencies
└── uploads/             # Created automatically by LocalStorage
    ├── avatars/
    ├── data/
    ├── gallery/
    ├── images_only/
    ├── resumes/
    └── users/
```

-----

## 📖 API Endpoints Guide

Here is a full list of all available endpoints, what they do, and how to test them using `curl`.

**Note:** For `curl` commands, create a dummy file to upload, e.g., `echo "test file" > test.txt` or `echo "test image" > test.jpg`.

### 1\. Basic Local Upload

  * **Endpoint:** `POST /upload/`
  * **Description:** Uploads a single file to the `./uploads/` directory.
  * **Form Field:** `file`
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload/" \
         -F "file=@test.txt"
    ```

### 2\. Multi-File Local Upload

  * **Endpoint:** `POST /upload-gallery/`
  * **Description:** Uploads up to 10 files to `./uploads/gallery/`.
  * **Form Field:** `gallery_images`
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-gallery/" \
         -F "gallery_images=@test.txt" \
         -F "gallery_images=@test.jpg"
    ```

### 3\. Multi-Field Local Upload

  * **Endpoint:** `POST /upload-profile/`
  * **Description:** Uploads files from two different fields (`avatar` and `resume`) to separate directories.
  * **Form Fields:** `avatar` (required), `resume` (optional)
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-profile/" \
         -F "avatar=@test.jpg" \
         -F "resume=@test.txt"
    ```

### 4\. In-Memory Upload

  * **Endpoint:** `POST /upload-memory/`
  * **Description:** Uploads a single file directly into memory (bytes). The file is not saved to disk.
  * **Form Field:** `profile_pic`
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-memory/" \
         -F "profile_pic=@test.jpg"
    ```

### 5\. S3 Upload

  * **Endpoint:** `POST /upload-s3/`
  * **Description:** Uploads a single file to your S3 bucket under the `user-uploads/` prefix.
  * **Form Field:** `document`
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-s3/" \
         -F "document=@test.txt"
    ```

### 6\. Dynamic Path Upload

  * **Endpoint:** `POST /upload-dynamic-path/`
  * **Description:** Uploads a file to a dynamic local path based on a request header (`X-User-ID`).
  * **Form Field:** `user_file`
  * **Test:** (This will save to `uploads/users/user_123/`)
    ```bash
    curl -X POST "http://localhost:8000/upload-dynamic-path/" \
         -H "X-User-ID: user_123" \
         -F "user_file=@test.txt"
    ```

### 7\. Renamed File Upload

  * **Endpoint:** `POST /upload-renamed/`
  * **Description:** Uploads a file to `./uploads/data/` but renames it to a unique UUID while keeping the extension.
  * **Form Field:** `data`
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-renamed/" \
         -F "data=@test.jpg"
    ```

### 8\. Filtered Upload

  * **Endpoint:** `POST /upload-image-only/`
  * **Description:** Only accepts up to 4 files that are `image/jpeg` or `image/png` and are not empty. Other files are rejected.
  * **Form Field:** `image`
  * **Test (Success):**
    ```bash
    # (Assuming test.jpg is a real JPEG)
    curl -X POST "http://localhost:8000/upload-image-only/" \
         -F "image=@test.jpg"
    ```
  * **Test (Failure):**
    ```bash
    # (This file will be rejected by the filter)
    curl -X POST "http://localhost:8000/upload-image-only/" \
         -F "image=@test.txt"
    ```

### 9\. Multi-Engine Upload

  * **Endpoint:** `POST /upload-all-at-once/`
  * **Description:** A single request that uploads files to three different backends:
      * `avatar` -\> Local Disk (`uploads/avatars/`)
      * `resume` -\> Amazon S3 (`resumes/` prefix in your bucket)
      * `config_file` -\> In-Memory
  * **Form Fields:** `avatar` (required), `resume` (optional), `config_file` (optional)
  * **Test:**
    ```bash
    curl -X POST "http://localhost:8000/upload-all-at-once/" \
         -F "avatar=@test.jpg" \
         -F "resume=@test.txt" \
         -F "config_file=@test.txt"
    ```

-----
