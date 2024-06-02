import os
import requests
import json
import boto3
from botocore.exceptions import ClientError
import pymupdf


def get_parameters():
    response = ssm.get_parameters(Names=["LambdaSecureString"], WithDecryption=True)
    for parameter in response["Parameters"]:
        return parameter["Value"]


def upload_file_to_s3(file_name, bucket=settings.AWS_STORAGE_BUCKET_NAME, object_name=None) -> bool:
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
        s3_client.upload_file(file_name, bucket, object_name)
        return True
    except ClientError as e:
        return False


def process_signed_form(self, event: dict) -> bool:
    """
    Process a signed form by downloading the document, saving it locally, and uploading it to object storage.

    Args:
        docseal_payload (dict): A dictionary containing information about the signed form.

    Returns:
        bool: An HTTP response indicating the success or failure of the process.

    Raises:
        requests.RequestException: If there is an issue with downloading the file.
        Exception: If there is a general error during the process.
    """
    if not isinstance(event, dict):
        docseal_payload = json.loads(event)
    else:
        docseal_payload = event

    try:
        # Use dictionary unpacking to reduce repeated key access
        document_data = docseal_payload["documents"]
        employee_data = docseal_payload["data"]

        document_type = document_data["name"].split("_")[0]
        employee = Employee.objects.select_related("last_name", "first_name").get(employee_id=employee_data["external_id"])

        # Use f-strings for more efficient string formatting
        pre_file = f"{document_type}/{document_type}-{employee.last_name}_{employee.first_name}.pdf"
        file_name = f"attestations/{document_type}/{document_data['name'].split('_')[0]}-{employee.last_name}_{employee.first_name}.pdf"

        # Use the `requests` library's built-in error handling
        response = requests.get(document_data["submission"]["url"], timeout=10)

        response.raise_for_status()  # Raise an exception for bad status codes

        with open(file_name, "wb") as file:
            file.write(response.content)

        logger.info("File downloaded successfully!")

        # Use `pymupdf` more efficiently by avoiding unnecessary file I/O
        with pymupdf.open(pre_file) as doc:
            doc.save(file_name, linear=True)
            if upload_file_to_s3(file_name=file_name):
                logger.success(
                    f"SUCCESS: PROCESSED SIGNED {document_type} for {employee.last_name}, {employee.first_name.split()[0]} - signed form persisted in object storage with the fikle nbame of {file_name}",
                    status=status.HTTP_201_CREATED,
                )
                return HttpResponse(
                    content=f"SUCCESS: PROCESSED SIGNED {document_type} for {employee.last_name}, {employee.first_name.split()[0]} - signed form persisted in object storage with the fikle nbame of {file_name}",
                    status=status.HTTP_201_CREATED,
                )
            else:
                logger.error()
                return HttpResponse(
                    content=f"FAILED: UNABLE T PROCESSED SIGNED {document_type} for {employee.last_name}, {employee.first_name.split()[0]} - signed form persisted in object storage with the fikle nbame of {file_name}",
                    status=status.HTTP_201_CREATED,
                )
    except requests.RequestException as e:
        logger.warning("Failed to download the file.")
        return HttpResponse(content=f"ERROR: FAILED TO PROCESS SIGNED {document_type} for {employee.last_name}, {employee.first_name.split()[0]} - {e}", status=status.HTTP_417_EXPECTATION_FAILED)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(content=f"ERROR: FAILED TO PROCESS SIGNED {document_type} for {employee.last_name}, {employee.first_name.split()[0]} - {e}", status=status.HTTP_417_EXPECTATION_FAILED)
