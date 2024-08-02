import io
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from compliance.models import Compliance
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from employee.models import Employee

from nhhc.utils.upload import UploadHandler  # Replace with the actual module name

# class TestUploadHandler(unittest.TestCase):
#     def setUp(self):
#         # Create a sample Employee for testing
#         self.sample_employee = Employee(
#             first_name="John", last_name="Doe", hire_date=datetime.now()
#         )

#     def test_generate_randomized_file_name(self):
#         initial_file_name = "example.txt"
#         result = UploadHandler.generate_randomized_file_name(
#             initial_file_name, self.sample_employee
#         )

#         # Ensure the result is not empty
#         self.assertTrue(result)

#         # Check if the result contains the uploader's first name as a prefix
#         self.assertTrue(result.startswith(self.sample_employee.first_name.lower()))

#         # Check if the result contains the file extension
#         self.assertTrue(result.endswith(initial_file_name.split(".")[-1]))

#     @patch("builtins.open", new_callable=io.StringIO)
#     @patch("magic.from_buffer", return_value=settings.FILER_MIME_TYPE_WHITELIST[0])
#     def test_validate_mime_type_allowed(self, mock_from_buffer, mock_open):
#         file_name = "example.txt"
#         file_content = "Example file content"
#         file_object = io.StringIO(file_content)

#         result = UploadHandler.validate_mime_type(file_name, file_object)

#         # Ensure the result is True for allowed MIME type
#         self.assertTrue(result)

#     @patch("builtins.open", new_callable=io.StringIO)
#     @patch("magic.from_buffer", return_value="invalid/mimetype")
#     def test_validate_mime_type_not_allowed(self, mock_from_buffer, mock_open):
#         file_name = "example.txt"
#         file_content = "Example file content"
#         file_object = io.StringIO(file_content)

#         with self.assertRaises(FileValidationError):
#             UploadHandler.validate_mime_type(file_name, file_object)

#     @patch("builtins.open", new_callable=io.StringIO)
#     def test_validate_filecontents_allowed(self, mock_open):
#         file_name = "example.txt"
#         file_content = "Example file content"
#         file_object = io.StringIO(file_content)

#         result = UploadHandler.validate_filecontents(file_name, file_object)

#         # Ensure the result is True for allowed contents
#         self.assertTrue(result)

#     @patch("builtins.open", new_callable=io.StringIO)
#     def test_validate_filecontents_not_allowed(self, mock_open):
#         file_name = "example.txt"
#         file_content = "Example <script>alert('Hello');</script> content"
#         file_object = io.StringIO(file_content)

#         with self.assertRaises(FileValidationError):
#             UploadHandler.validate_filecontents(file_name, file_object)


# if __name__ == "__main__":
#     unittest.main()
