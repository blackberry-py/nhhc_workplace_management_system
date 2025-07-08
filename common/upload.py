"""
Module: upload_handler.py

This module contains classes and functions related to handling file uploads and downloads, specifically to and from an S3 bucket.

Classes:
- FileValidationError: Custom exception for file validation errors.
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

import os
import sys
import threading

import boto3
import requests
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadhandler import FileUploadHandler
from django.utils.deconstruct import deconstructible
from loguru import logger

from common.metrics import metrics


@deconstructible
class UploadHandler(FileUploadHandler):
    def __init__(self, upload_type):
        self.s3_path = upload_type
        self.s3_client = boto3.client(
            "s3",
            region_name=os.environ["AWS_S3_REGION_NAME"],
            endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
            aws_access_key_id=os.environ["AWS_SES_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )

    def receive_data_chunk(self, raw_data, start):
        pass

    def generate_randomized_file_name(
        self,
        instance,
        filename: str,
    ) -> os.PathLike | str:
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


class ProgressPercentage:

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
            sys.stdout.write(f"\r{self._filename}  {self._seen_so_far} / {self._size}  ({percentage:.2f}%)")
            sys.stdout.flush()


class S3HANDLER(FileSystemStorage):
    @staticmethod
    @metrics.s3_upload_recorder.time()
    def upload_file_to_s3(file_name, bucket: str = settings.AWS_STORAGE_BUCKET_NAME, object_name=None) -> bool:
        """
        Upload a file to an S3 bucket
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
        s3_client = boto3.client(
            "s3",
            region_name=os.environ["AWS_S3_REGION_NAME"],
            endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        try:
            s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name))
            return True
        except ClientError:
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
    @metrics.docuseal_download_recorder.time()
    def download_pdf_file(payload: dict) -> bool:
        """
        Download PDF from given URL to local directory.

        :param url: The url of the PDF file to be downloaded
        :return: True if PDF file was successfully downloaded, otherwise False.
        """

        # Request URL and get response object
        response = requests.get(payload["data"]["documents"][0]["url"], stream=True, timeout=30)

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
