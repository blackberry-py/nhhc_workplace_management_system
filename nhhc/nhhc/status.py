import datetime
import hashlib
import json
import os
import random
import re
import time
from collections import Counter
from contextlib import suppress
from os import PathLike
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.client import Redis
from redis.exceptions import (
   BusyLoadingError,
   ConnectionError,
   TimeoutError
)
import boto3
import psycopg2
import redis
import requests
from django.conf import settings
from faker import Faker
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable
from health_check.storage.backends import StorageHealthCheck
from loguru import logger

from nhhc.backends.storage_backends import PrivateMediaStorage

Faker.seed(time.time())
mock_data = Faker()


class DocSealSigningServiceHealthCheck(BaseHealthCheckBackend):
    critical_service = True
    base_url = "https://api.docuseal.co"
    submission_format = json.loads(
        """{
  "template_id": 340013,
  "send_email": false,
  "send_sms": false,
  "order": "preserved",
  "completed_redirect_url": "",
  "bcc_completed": "",
  "reply_to": "string",
  "expire_at": "2024-09-01 12:00:00 UTC",
  "message": {
    "subject": "Healthcheck Service Check",
    "body": "This is a submission created by Application Healthcheck....Checking the status of the Docseal Service"
  },
  "submitters": [
    {  "name": "",
    "phone": "",
    "email":"",
      "role": "First Party",
      "values": {},
      "external_id": "string",
      "completed": true,
      "metadata": {},
      "send_email": false,
      "send_sms": false,
      "completed_redirect_url": "",
      "fields": [
        {
          "name": "Health Check",
          "description": "string",
          "default_value": true,
          "invalid_message": " ",
          "readonly": false
        }
      ]
    }
  ]
}"""
    )

    def randomize_data(self) -> str:
        """
        Randomizes the data for a submission in the DocSealSigningServiceHealthCheck.

        This function updates the submission format by setting a new expiration date and randomizing the submitter's name, email, phone number, and external ID using mock data. It returns the updated submission data as a string.

        Returns:
            str: A string representation of the updated submission data.
        """
        submission = DocSealSigningServiceHealthCheck.submission_format
        submission["expire_at"] = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y-%m-%d  %H:%M:%S UTC")
        submission["reply_to"] = mock_data.email()

        submitter_details = submission["submitters"][0]
        submitter_details["name"] = mock_data.name()
        submitter_details["email"] = mock_data.email()
        # submitter_details["phone"] = "+14439835591",

        submitter_details["external_id"] = str(random.randint(8000, 12124445555444))
        return json.dumps(submission)

    def create_docseal_submission(self) -> int:
        """
        Creates a submission in the DocuSeal service using randomized data.

        This function prepares the necessary headers and payload for the submission request, then sends a POST request to the DocuSeal API. It returns the response text if the submission is successful, or None if the submission fails.

        Returns:
            str: The response text from the DocuSeal API if the submission is successful, otherwise None.

        Raises:
            KeyError: If the environment variable "DOCSEAL_TEST_API_KEY" is not set.
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": os.environ["DOCSEAL_TEST_API_KEY"]}
        payload = self.randomize_data()
        logger.debug(payload)
        response = (requests.request("POST", os.path.join(DocSealSigningServiceHealthCheck.base_url, "submissions"), headers=headers, data=payload)).json()
        logger.debug(response)
        if isinstance(response, dict) and "error" in response:
            return None
        if isinstance(response, list) and len(response) > 0:
            return int(response[0].get("submission_id", None))

        return None

    def archive_submission(self, submission_id: int) -> bool:
        """
        Archives a submission in the DocuSeal service using its submission ID.

        This function sends a DELETE request to the DocuSeal API to archive the specified submission. It returns True if the archiving is successful, otherwise it returns False.

        Args:
            submission_id (int): The ID of the submission to be archived.

        Returns:
            bool: True if the submission is successfully archived, otherwise False.

        Raises:
            KeyError: If the environment variable "DOCSEAL_TEST_API_KEY" is not set.
        """
        headers = {"X-Auth-Token": os.environ["DOCSEAL_TEST_API_KEY"]}
        response = (requests.request("DELETE", os.path.join(DocSealSigningServiceHealthCheck.base_url, "submissions", str(submission_id)), headers=headers)).json()
        logger.debug(response)
        return response["archived_at"] is not None

    def check_status(self):
        """
        Checks the status of a submission by creating and archiving it.

        This function attempts to create a submission using the DocuSeal service and, if successful, archives the submission. It returns True if the submission is successfully archived, otherwise it raises a ServiceUnavailable exception.

        Returns:
            bool: True if the submission is successfully archived.

        Raises:
            ServiceUnavailable: If there is an error during the submission creation or archiving process.
        """
        try:
            created_submission = self.create_docseal_submission()
            if created_submission != None:
                return self.archive_submission(created_submission)
        except Exception as e:
            logger.exception(str(e))
            raise ServiceUnavailable(message=f"Docuseal Service Is Offline. Unable to Create or Archive Submissions - {str(e)}") from e

    def identifier(self):
        return self.__class__.__name__


class CloudObjectStorageBackend(BaseHealthCheckBackend):

    def check_s3_health(self):
        """Check the health of an S3 bucket."""
        try:
            s3 = boto3.client(
                "s3", region_name=settings.AWS_S3_REGION_NAME, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            return {"s3": "healthy"}
        except Exception as e:
            logger.error(f"S3 health check failed: {e}")
            raise ServiceUnavailable(message=f"S3 Storage is unhealthy. Error: {str(e)}")

    def check_status(self):
        """Perform all health checks and return a summary."""
        return self.check_s3_health()
        
