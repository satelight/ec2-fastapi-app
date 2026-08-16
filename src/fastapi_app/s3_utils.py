import boto3
from botocore.exceptions import ClientError
import os

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "fastapi-files-20260816")
S3_REGION = "ap-northeast-1"

s3_client = boto3.client("s3", region_name=S3_REGION)


def upload_to_s3(file_path: str, s3_key: str) -> bool:
    """ローカルファイルを S3 にアップロード"""
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        return True
    except ClientError as e:
        print(f"Upload error: {e}")
        return False


def download_from_s3(s3_key: str, file_path: str) -> bool:
    """S3 からファイルをダウンロード"""
    try:
        s3_client.download_file(S3_BUCKET_NAME, s3_key, file_path)
        return True
    except ClientError as e:
        print(f"Download error: {e}")
        return False


def delete_from_s3(s3_key: str) -> bool:
    """S3 からファイルを削除"""
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        print(f"Delete error: {e}")
        return False


def list_s3_objects() -> list:
    """S3 バケット内のファイル一覧を取得"""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        if "Contents" not in response:
            return []
        return [obj["Key"] for obj in response["Contents"]]
    except ClientError as e:
        print(f"List error: {e}")
        return []
