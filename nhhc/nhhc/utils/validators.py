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
import random
import re
import string
import typing

import magic
from compliance.models import Compliance
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from employee.models import Employee
from filer.validation import FileValidationError


class UploadHandler:
    @staticmethod
    def determine_file_path():
        pass

    @staticmethod
    def generate_randomized_file_name(initial_file_name: str, uploader: Employee) -> str:
        """
        Static  method that Generate a randomized file name based on the uploader's information.

        Args:
            initial_file_name (str): The original file name.
            uploader (Employee): The employee who uploaded the file.

        Returns:
            str: A new file name with a unique combination of uploader-specific information and a random UUID.
        """
        uploader_specific_prefix = uploader.first_name.lower()
        suffix = str(uploader.hire_date) + "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(12))
        file_extension = initial_file_name.split(".")[-1]
        return f"{uploader_specific_prefix}{suffix}.{file_extension}"

    @staticmethod
    def validate_mime_type(file_name: str, file: typing.IO) -> bool:
        """
        Validate the MIME type of a file against the whitelist of allowed MIME types, configured in the settings module.

        Args:
            file_name (str): The name of the file being validated.
            file (typing.IO): The file object to be validated.

        Returns:
            bool: True if the file's MIME type is allowed, False otherwise.

        Raises:
            FileValidationError: If the file's MIME type does not match the allowed MIME types.
        """
        allowed_mime_type = settings.FILER_MIME_TYPE_WHITELIST

        # Open the file in binary mode
        with open(file, "rb") as file:
            # Use the magic library to determine the file's content type
            content_type = magic.from_buffer(file.read(1024), mime=True)

        # Check if the file's content type matches the allowed MIME type
        if content_type in allowed_mime_type:
            return True
        else:
            raise FileValidationError(_('File "{}": Upload rejected since file fails MIMETYPE check').format(file_name))

    @staticmethod
    def validate_filecontents(file_name: str, file: typing.IO) -> bool:
        """Validate the contents of a file against a list of disallowed code snippets.
        Args:
            file_name (str): The name of the file being validated.
            file (typing.IO): The file object to be validated.

        Raises:
            FileValidationError: If the file's contents match any of the disallowed code snippets.
        """
        disallowed_code_snippets = [
            r"<script\b[^>]*>([\s\S]*?)<\/script>",  # JavaScript
            r"<\?[\s\S]*?\?>",  # PHP
            r'<script\s+runat=["\']server["\']',  # ASP.NET
            r"--.*?--",  # SQL comment
            r"/\*.*?\*/",  # SQL comment
            r"CREATE\s+TABLE",  # SQL create table
            r"INSERT\s+INTO",  # SQL insert
            r"UPDATE\s+SET",  # SQL update
            r"DELETE\s+FROM",  # SQL delete
            r"DROP\s+TABLE",  # SQL drop table
        ]

        # Open the file in text mode
        with open(file, "r") as f:
            # Read the file's contents
            contents = f.read()

            # Check if the file's contents match any of the disallowed code snippets
            for snippet in disallowed_code_snippets:
                if re.search(snippet, contents):
                    raise FileValidationError(_('File "{}": Upload rejected since file fails content check').format(file_name))
