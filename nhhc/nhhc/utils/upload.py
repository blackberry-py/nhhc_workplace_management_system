"""
Module: upload_handler.py

This module contains classes and functions related to handling file uploads and downloads, specifically to and from an S3 bucket.

Classes:
- FileValidationError: Custom exception for file validation errors.
- FileValidator: Class for validating file properties such as size and content type.
- UploadHandler: Class for handling file uploads to S3 with customized file naming.
- ProgressPercentage: Class for tracking upload progress.
- S3HANDLER: Class for uploading and downloading files to and from S3.

Functions:
- S3HANDLER.upload_file_to_s3: Uploads a file to an S3 bucket.
- S3HANDLER.generate_filename: Generates a filename based on payload data.
- S3HANDLER.download_pdf_file: Downloads a PDF file from a URL and uploads it to S3.

Usage:
Import the module and utilize the classes and functions for handling file uploads and downloads to and from an S3 bucket.

"""

import json
import os
import random
import re
import string
import sys
import threading
import typing

import boto3
import requests
from botocore.exceptions import ClientError
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from filetype import guess
from loguru import logger
from prometheus_client import Histogram

from nhhc.utils.metrics import MetricsRecorder

s3_upload_recorder = Histogram("s3_upload_duration", "Metric of the Durtation of S3 upload of Compliance Documents from the application's /tmp to AWS S3 block storage.")
docuseal_download_recorder = Histogram("docuseal_download_duration", "Metric of the Durtation of downloading singed  Compliance Documents from the DocSeal External Signing Service to /tmp storage.")


class FileValidationError(AttributeError):
    """Custom exception for file validation errors."""

    pass


@deconstructible
class FileValidator(object):
    error_messages = {
        "max_size": ("Ensure this file size is not greater than %(max_size)s." " Your file size is %(size)s."),
        "min_size": ("Ensure this file size is not less than %(min_size)s. " "Your file size is %(size)s."),
        "content_type": "Files of type %(content_type)s are not supported.",
    }

    def __init__(self, max_size: typing.Optional[int] = None, min_size: typing.Optional[int] = None, content_types: set = ()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                "max_size": filesizeformat(self.max_size),
                "size": filesizeformat(data.size),
            }
            raise FileValidationError(self.error_messages["max_size"], "max_size", params)

        if self.min_size is not None and data.size < self.min_size:
            params = {"min_size": filesizeformat(self.min_size), "size": filesizeformat(data.size)}
            raise FileValidationError(self.error_messages["min_size"], "min_size", params)

        if self.content_types:
            file = guess(data)
            file_type = file.mime

        if file_type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
            raise FileValidationError(self.error_messages["content_type"], "content_type", params)

    def __eq__(self, other):
        return isinstance(other, FileValidator) and self.max_size == other.max_size and self.min_size == other.min_size and self.content_types == other.content_types


@deconstructible
class UploadHandler:
    def __init__(self, upload_type):
        self.s3_path = upload_type

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


class S3HANDLER:
    @staticmethod
    @s3_upload_recorder.time()
    def upload_file_to_s3(file_name, bucket: str = settings.AWS_STORAGE_BUCKET_NAME, object_name=None) -> bool:
        """Upload a file to an S3 bucket
        Args:
            file_name: File to upload
            bucket: Bucket to upload to
            object_name: S3 object name. If not specified then file_name is used
        Returns:
            bool  - True if file was uploaded, else False
        """
        if object_name is None:
            object_name = file_name
            logger.debug(object_name)
            logger.debug(file_name)

        # Upload the file
        s3_client = boto3.client("s3",
                region_name='nyc3',
                endpoint_url='https://nyc3.digitaloceanspaces.com',
                aws_access_key_id=os.environ["SPACES_KEY"],
                aws_secret_access_key=os.environ["SPACES_SECRET"]
                                 )
        try:
            s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name))
            return True
        except ClientError as e:
            return False

    @staticmethod
    def get_doc_type(document_id: int) -> str:
        match document_id:
            case 90907:
                return "do_not_drive_agreement_attestation"
            case 101305:
                return "state_w4_attestation"
            case 91067:
                return "dha_i9"
            case 90909:
                return "hca_policy_attestation"
            case 90908:
                return "doa_agency_policies_attestation"
            case 90910:
                return "job_duties_attestation"
            case 116255:
                return "idph_background_check_authorization"
            case _:
                return "unknown"

    @staticmethod
    def generate_filename(payload: dict) -> str:
        employee_upload_suffix = f"{payload['data']['metadata']['last_name'].lower()}_{payload['data']['metadata']['first_name'].lower()}.pdf"
        document_id = payload["data"]["template"]["id"]
        doc_type_prefix = S3HANDLER.get_doc_type(document_id)

        path = os.path.join("restricted", "attestations", doc_type_prefix)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, f"{doc_type_prefix}_{employee_upload_suffix}")

    @staticmethod
    @docuseal_download_recorder.time()
    def download_pdf_file(payload: dict) -> bool:
        """Download PDF from given URL to local directory.

        :param url: The url of the PDF file to be downloaded
        :return: True if PDF file was successfully downloaded, otherwise False.
        """

        # Request URL and get response object
        response = requests.get(payload["data"]["documents"][0]["url"], stream=True)

        # isolate PDF filename from URL
        pdf_file_name = S3HANDLER.generate_filename(payload)

        if response.status_code == 200:
            # Save in current working directory
            with open(pdf_file_name, "wb+") as pdf_object:
                pdf_object.write(response.content)
                S3HANDLER.upload_file_to_s3(pdf_file_name)
                logger.info(f"{pdf_file_name} was successfully saved!")
                return True
        else:
            print(f"Uh oh! Could not download {pdf_file_name},")
            print(f"HTTP response status code: {response.status_code}")
            return False
