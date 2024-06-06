"""
module: nhhc.utils.validators

Module for handling file uploads and validation.

This module contains a class UploadHandler with static methods for generating randomized file names, validating MIME types, and validating file contents against a list of disallowed code snippets.

Attributes:
    - UploadHandler: A class for handling file uploads and validation.

Methods:
    - generate_randomized_file_name(initial_file_name: str, uploader: Employee) -> str: Generates a randomized file name based on the uploader's information.
    - validate_mime_type(file_name: str, file: typing.IO) -> bool: Validates the MIME type of a file against the whitelist of allowed MIME types.
    - validate_filecontents(file_name: str, file: typing.IO) -> bool: Validates the contents of a file against a list of disallowed code snippets.
"""

import os
import random
import re
import string
import typing

import magic
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from filetype import guess
from loguru import logger


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
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)
            file = guess(data)
            type = file.mime

            if content_type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
                params = {"content_type": content_type}
                raise FileValidationError(self.error_messages["content_type"], "content_type", params)
            elif type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
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
