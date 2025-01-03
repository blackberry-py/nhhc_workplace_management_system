"""
Module: nhhc.utils.upload

This module contains classes and functions related to handling file uploads and downloads, specifically to and from an S3 bucket.

Classes:
- FileValidationError: Custom exception for file validation errors.
- UploadHandler: Class for handling file uploads to S3 with customized file naming.
- ProgressPercentage: Class for tracking upload progress.

Functions:
- download_and_upload_pdf: Downloads file from URL to Memory and Uploads to an S3 bucket.
- generate_filename: Generates a filename based on payload data.

Usage:
Import the module and utilize the classes and functions for handling file uploads and downloads to and from an S3 bucket.

"""

import os
import sys
import threading
import typing

import boto3
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from loguru import logger

from nhhc.utils.helpers import (
    _confirm_docseal_payload,
    _download_file_to_memory,
    _extract_template_id,
    _extract_uploading_employee_name,
    _generate_filename_from_parts,
    _get_doc_type,
    _upload_file_to_s3,
    _validate_docseal_payload,
    _validate_file_metadata,
    FileValidationError
)
from nhhc.utils.metrics import metrics


@deconstructible
class UploadHandler:
    def __init__(self, upload_type):
        self.s3_path = upload_type
        self.s3_client = boto3.client(
            "s3",
            region_name=os.environ["AWS_S3_REGION_NAME"],
            endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
            aws_access_key_id=os.environ["AWS_SES_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )

    def generate_randomized_file_name(
        self,
        instance,
        filename: str,
    ) -> typing.Union[os.PathLike, str]:
        """
        Static  method that Generate a randomized file name based on the uploader's information.

        Args:
            filename (str): The original file name.
            instance (Employee): The employee who uploaded the file.

        Returns:
            os.PathLike object or str: A new file name with a unique combination of uploader-specific information and a random UUID.
        """
        file_extension = filename.split(".")[-1]
        uploader_specific_prefix = f"{instance.last_name.lower()}_{instance.first_name.lower()}"
        filename = f"{uploader_specific_prefix}.{file_extension}"
        final_path = os.path.join(self.s3_path, filename)
        logger.debug(final_path)
        return final_path

    def __eq__(self, other):
        return isinstance(other, UploadHandler) and self.s3_path == other.s3_path


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()


def generate_filename(payload: typing.Dict) -> str:
    """Generates a filename based on the provided payload.

    Extracts data from the payload, validates it, and constructs a unique filename.

    Args:
        payload (dict): The payload containing data, metadata, and template information.

    Returns:
        str: The generated filename.
    """
    data = _confirm_docseal_payload(payload)
    metadata, template = _validate_docseal_payload(data)
    last_name, first_name = _extract_uploading_employee_name(metadata)
    document_id = _extract_template_id(template)
    doc_type_prefix = _get_doc_type(document_id)
    return _generate_filename_from_parts(doc_type_prefix, last_name, first_name)


@metrics.docuseal_download_recorder.time()
def download_and_upload_pdf(payload: typing.Dict, max_file_size_mb: int = 1) -> bool:
    """
    Downloads a PDF from a URL specified in the payload and uploads it to S3.

    Args:
        payload (Dict): Payload containing download information.
        max_file_size_mb (int, optional): Maximum file size in megabytes. Defaults to 1MB.

    Returns:
        bool: True if download and upload successful, False otherwise.
    """
    try:
        # Pre-check file metadata
        url = payload["data"]["documents"][0]["url"]
        _validate_file_metadata(url, max_file_size_mb)

        # Download file into memory
        file_obj = _download_file_to_memory(url)

        # Generate object name for S3 upload
        pdf_file_name = generate_filename(payload)

        if _upload_file_to_s3(file_obj, object_name=pdf_file_name):
            logger.success(f"Successfully uploaded {pdf_file_name}")
            return True
        else:
            logger.error(f"Failed to upload {pdf_file_name} to S3")
            return False
    except FileValidationError as fve:
        logger.error(f"Unable to Validate the File Before Downloading:{fve}")
        return False
    except ValueError as ve:
        logger.error(f"Unable to Verify the Data Quality or Contents of Payload: {ve}")
        return False
    except Exception as e:
        logger.error(f"Unable to Retrieve or Upload Attestation: {e}")
        return False
