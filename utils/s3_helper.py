import boto3
import os
import uuid
import base64

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        endpoint_url=os.getenv("S3_URL")
    )

def upload_base64_to_s3(base64_string, folder="images"):
    """
    Uploads a base64 encoded image to S3 and returns the public URL.
    """
    if not base64_string:
        return None

    # Strip metadata if present (e.g., "data:image/jpeg;base64,...")
    if ";base64," in base64_string:
        base64_string = base64_string.split(";base64,")[1]
    
    file_bytes = base64.b64decode(base64_string)
    filename = f"{folder}/{uuid.uuid4().hex}.jpg"
    bucket = os.getenv("S3_BUCKET_NAME")

    s3_client = get_s3_client()
    s3_client.put_object(
        Bucket=bucket,
        Key=filename,
        Body=file_bytes,
        ContentType="image/jpeg"
    )
    
    base_url = os.getenv("S3_URL", "").rstrip('/')
    return f"{base_url}/{bucket}/{filename}"

def upload_file_to_s3(file_bytes, content_type="image/jpeg", folder="images"):
    """
    Uploads raw file bytes to S3 and returns the public URL.
    """
    if not file_bytes:
        return None

    filename = f"{folder}/{uuid.uuid4().hex}.jpg"
    bucket = os.getenv("S3_BUCKET_NAME")

    s3_client = get_s3_client()
    s3_client.put_object(
        Bucket=bucket,
        Key=filename,
        Body=file_bytes,
        ContentType=content_type
    )
    
    base_url = os.getenv("S3_URL", "").rstrip('/')
    return f"{base_url}/{bucket}/{filename}"

def get_presigned_url(s3_url):
    """
    Given a raw S3 URL from the database, generates a temporary presigned URL.
    """
    if not s3_url or not isinstance(s3_url, str) or not s3_url.startswith("http"):
        return s3_url
        
    base_url = os.getenv("S3_URL", "").rstrip('/')
    bucket = os.getenv("S3_BUCKET_NAME")
    prefix = f"{base_url}/{bucket}/"
    
    if s3_url.startswith(prefix):
        key = s3_url[len(prefix):]
        try:
            client = get_s3_client()
            return client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600
            )
        except Exception as e:
            print("Error generating presigned URL:", e)
            return s3_url
    return s3_url
