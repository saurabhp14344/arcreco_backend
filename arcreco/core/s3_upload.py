import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from arcreco import settings


def create_presigned_post(bucket_name=settings.AWS_STORAGE_BUCKET_NAME, key=None, expiration=3600):
    """Create S3 image url"""
    s3_client = boto3.client("s3", config=Config(signature_version='s3v4'),
                             region_name="ap-south-1",
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             )
    try:
        response = s3_client.generate_presigned_post(Bucket=bucket_name,
                                                     Key=f'{key}',
                                                     Fields={"acl": "public-read", "Content-Type": 'image/jpg'},
                                                     Conditions=[
                                                         {"acl": "public-read"},
                                                         {"Content-Type": 'image/jpg'}
                                                     ],
                                                     ExpiresIn=expiration)
    except ClientError as e:
        return None
    return response
