import json
import boto3
import os
from botocore.exceptions import ClientError
import requests

client = boto3.client("events")


def lambda_handler(event, context) -> dict:
    try:
        request = requests.post(url=os.environ.get("APP_ENDPOINT"), json=json.dumps(event))
        response = client.put_events(
            Entries=[
                {"DetailType": "Newly Signed Docseal Document", "Detail": json.dumps(event), "EventBusName": os.environ.get("EVENT_BUS"), "Source": "docseal", "TraceHeader": "new_signing"},
            ]
        )
        return {"events": response, "request": {"status_code": request.status_code, "text": request.text}}
    except ClientError as err:
        print(err)
