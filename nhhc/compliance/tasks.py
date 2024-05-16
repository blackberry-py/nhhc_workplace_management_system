import logging
import boto3
from botocore.exceptions import ClientError
import os
import requests
import json
from celery import shared_task
from employee.models import Employee
from django.conf import settings
import pymupdf


def upload_file(file_name, bucket=settings.AWS_STORAGE_BUCKET_NAME, object_name=None) -> bool:
    """Upload a file to an S3 bucket
    Args:
        file_name: File to upload
        bucket: Bucket to upload to
        object_name: S3 object name. If not specified then file_name is used
    Returns:
        bool  - True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


@shared_task(
    bind=True,
    serializer="json",
)
def process_signed_form(self, docseal_payload: dict) -> bool:
    if not isinstance(docseal_payload, dict):
        docseal_payload = json.loads(docseal_payload)
    try:
        type = docseal_payload["documents"]["name"].split("_")[0]
        employee = Employee.objects.get(employee_id=docseal_payload["data"]["external_id"])
        pre_file = f"{type}/{type}-{employee.last_name}_{employee.first_name}.pdf"
        file_name = f"attestations/{type}/{docseal_payload['documents']['name'].split('_')[0]}-{employee.last_name}_{employee.first_name}.pdf"
        response = requests.get(docseal_payload["documents"]["submission"]["url"])

        if response.status_code == 200:
            with open(file_name, "wb") as file:
                file.write(response.content)

                print("File downloaded successfully!")
                doc = pymupdf.open(pre_file)
                doc.save(file_name, linear=True)
                upload_file(file_name=file_name)
        else:
            print("Failed to download the file.")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
