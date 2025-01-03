import io
import os
import typing
import uuid
from typing import Any, Dict, Tuple

import boto3
import requests
from botocore.exceptions import ClientError
from django.conf import settings
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from loguru import logger
from rest_framework import status

from nhhc.utils.metrics import metrics


class FileValidationError(ValidationError):
    pass


def get_status_code_for_unauthorized_or_forbidden(request: HttpRequest) -> int:
    """
    Determine the appropriate HTTP status code for unauthorized or forbidden requests.

    Utility Helper function takes in an HTTP request object and checks if the user associated with the request is authenticated.
    If the user is not authenticated, it returns HTTP status code 401 (Unauthorized). If the user is authenticated but
    does not have permission to access the requested resource, it returns HTTP status code 403 (Forbidden).

    Args:
        request (HttpRequest): An HTTP request object representing the request being processed.

    Returns:
        int: The HTTP status code to be returned based on the authentication status of the user.
    """
    return status.HTTP_403_FORBIDDEN if request.user.is_authenticated else status.HTTP_401_UNAUTHORIZED


def get_content_for_unauthorized_or_forbidden(request: HttpRequest) -> bytes:
    """
    Utility Helper function that returns a message based on the user's authentication status.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        bytes: A message indicating whether the user must be logged in or an admin to complete the request.
    """
    return bytes("You Must Be An Admin In To Complete This Request", "utf-8") if request.user.is_authenticated else bytes("You Must Be Logged In To Complete This Request", "utf-8")


#

# Section - Utility Functions for Upload.py


def _confirm_docseal_payload(payload: typing.Dict) -> Dict[str, Any]:
    """CONFIRMS the payload and extracts data.

        Checks if the payload is a non-empty dictionary and returns the "data" key's value.

        Args:
            payload (dict): The payload to validate.

        Returns:
    s       dict: The data extracted from the payload.

        Raises:
            ValueError: If the payload is invalid (not a non-empty dictionary).
    """
    if not payload or not isinstance(payload, dict):
        raise ValueError("Invalid payload: Must be a non-empty dictionary")
    return payload.get("data", {})


def _validate_docseal_payload(data: typing.Dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Validates the data and extracts metadata and template information.

    Checks if the provided data is a non-empty dictionary and returns the "metadata" and "template" key's values.

    Args:
        data (dict): The data dictionary to validate and extract from.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing the metadata and template dictionaries.

    Raises:
        ValueError: If the provided data is invalid (not a non-empty dictionary).
    """
    if not data or not isinstance(data, dict):
        raise ValueError("Invalid payload: 'data' must be a non-empty dictionary")
    return data.get("metadata", {}), data.get("template", {})


def _extract_uploading_employee_name(metadata: typing.Dict) -> Tuple[str, str]:
    """Extracts and formats the uploading employee's name from metadata.

    Retrieves the "last_name" and "first_name" from the metadata, converts them to lowercase, removes leading/trailing whitespace, and returns them as a tuple.

    Args:
        metadata (dict): The metadata dictionary containing employee information.

    Returns:
        Tuple[str, str]: A tuple containing the employee's last and first name.


    Raises:
        ValueError: If metadata is invalid (not a non-empty dictionary) or if "last_name" or "first_name" are missing or empty.
    """

    if not metadata or not isinstance(metadata, dict):
        raise ValueError("Invalid payload: 'metadata' must be a non-empty dictionary")
    last_name = metadata.get("last_name", "").lower().strip()
    first_name = metadata.get("first_name", "").lower().strip()
    if not last_name or not first_name:
        raise ValueError("Missing required metadata: 'last_name' and 'first_name' must be non-empty")
    return last_name, first_name


def _extract_template_id(template: typing.Dict) -> int:
    """Validates the template and extracts the document ID.

    Checks for the existence of the "id" key within the template and returns its integer representation.

    Args:
        template (dict): The template dictionary.

    Returns:
        int: The document ID.

    Raises:
        ValueError: If the template is missing the "id" key.
    """
    document_id = template.get("id")
    if document_id is None:
        raise ValueError("Missing required template ID")
    return int(document_id)


def _get_doc_type(document_id: int) -> str:
    """Retrieves the document type string associated with a given document ID.

    Uses the `DOCSEAL_DOCUMENT_TYPES` enum to fetch the string value corresponding to the provided ID.

    Args:
        document_id (int): The ID of the document.

    Returns:
        str: The document type string.
    """
    return settings.DOCSEAL_DOCUMENT_TYPES[document_id].value


def _generate_filename_from_parts(doc_type_prefix: str, last_name: str, first_name: str) -> str:
    """Generates a unique filename based on provided parts.

    Constructs a filename using the document type prefix, last name, first name, and a UUID, then creates a full path including subdirectories.

    Args:
        doc_type_prefix (str): The prefix for the document type.
        last_name (str): The employee's last name.
        first_name (str): The employee's first name.

    Returns:
        str: The full path to the generated filename.
    """
    unique_id = uuid.uuid4()
    filename = f"{doc_type_prefix}_{last_name}_{first_name}_{unique_id}.pdf"
    return os.path.join("restricted", "attestations", doc_type_prefix, filename)


def _validate_file_metadata(url: str, max_file_size_mb: int) -> typing.Tuple[int, str]:
    """Validates file metadata by checking content length, type, and size.

    Retrieves file metadata from a URL and validates it against
    predefined criteria, including maximum file size and allowed MIME types.


    Args:
        url (str): The URL of the file to validate.
        max_file_size_mb (int): The maximum allowed file size in MB.

    Returns:
        Tuple[int, str]: A tuple containing the content length and content type.

    Raises:
        FileValidationError: If the file metadata is invalid or the file size exceeds the maximum limit.
    """
    pre_check_response = requests.head(url)
    content_length = int(pre_check_response.headers.get("Content-Length", 0))
    content_type = pre_check_response.headers.get("Content-Type", None)

    # Validate file metadata
    if content_length == 0 or content_type is None:
        logger.error(f"Incoming File Metadata Errors: Content-Length must be greater than zero: {content_length}, and Content-Type must be provided: {content_type}")
        raise FileValidationError(f"Invalid file metadata: Content-Length {content_length}, Content-Type {content_type}")

    file_size_mb = content_length / (1024 * 1024)

    if file_size_mb > max_file_size_mb:
        logger.warning(f"File size {file_size_mb:.2f} MB exceeds maximum limit of {max_file_size_mb} MB")
        raise FileValidationError(f"File size {file_size_mb:.2f} MB exceeds maximum limit of {max_file_size_mb} MB")

    if content_type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
        raise FileValidationError(f"Invalid file type {content_type}. Allowed types are: {', '.join(settings.ALLOWED_UPLOAD_MIME_TYPES)}")

    return content_length, content_type


@metrics.docuseal_download_recorder.time()
def _download_file_to_memory(url: str) -> io.BytesIO:
    """Downloads a file from a URL and stores it in memory.

    Retrieves a file from the specified URL and stores it in a BytesIO object.

    Args:
        url (str): The URL of the file to download.

    Returns:
        io.BytesIO: A BytesIO object containing the downloaded file data.

    Raises:
        FileValidationError: If the file download fails (status code not 200).

    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        logger.error(f"Failed to download file. Status code: {response.status_code}")
        raise FileValidationError(f"Failed to download file with status code {response.status_code}")

    file_obj = io.BytesIO()
    for chunk in response.iter_content(chunk_size=8192):
        file_obj.write(chunk)
    file_obj.seek(0)  # Reset cursor before upload

    return file_obj


def _upload_file_to_s3(file_obj, bucket: str = settings.AWS_STORAGE_BUCKET_NAME, object_name: str = None) -> bool:
    """Uploads an in-memory file to an S3 bucket."""
    s3_client = boto3.client(
        "s3",
        region_name=os.environ.get("AWS_S3_REGION_NAME"),
        endpoint_url=os.environ.get("AWS_S3_ENDPOINT_URL"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        s3_client.upload_fileobj(file_obj, bucket, object_name)
        logger.info(f"Uploaded to S3 bucket '{bucket}' as '{object_name}'")
        return True
    except ClientError as e:
        logger.exception(f"Error uploading to S3: {e}")
        return False
