import boto3
from django.conf import settings
from django.http import HttpResponse
from botocore.exceptions import NoCredentialsError, ClientError

def upload_to_s3(file, file_path):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        print("S3 bucket:", settings.AWS_STORAGE_BUCKET_NAME)
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_path,
            ExtraArgs={
                # 'ACL': 'public-read',  # Make file public; change as needed
                'ContentType': file.content_type  # Set appropriate content type
            }
        )
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}"
        return file_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None


def download_from_s3(file_path, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    try:
        s3_object = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
        
        # Get the file content from S3
        file_content = s3_object['Body'].read()

        # Create a response object and set the content type and headers for file download
        response = HttpResponse(file_content, content_type=s3_object['ContentType'])
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    except NoCredentialsError:
        print("Credentials not available")
        return None
    except ClientError as e:
        print(f"Error occurred: {str(e)}")
        return None