
import json
import os
import boto3
import pymupdf
import requests
from botocore.exceptions import ClientError

def upload_file_to_s3(file_name:str, bucket:str="nhhc_chicago", object_name=None) -> bool:
    """Upload a file to an S3 bucket
    Args:
        file_name: File to upload
        bucket: Bucket to upload to
        object_name: S3 object name. If not specified then file_name is used
    Returns:
        bool  - True if file was uploaded, else False
    """

    # If S3 object_name was noMason250
    #
    # Mspecified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        return True
    except ClientError as e:
        return False


def generate_filename(payload:dict) ->  os.PathLike:
    employee_upload_suffix = f"{payload['data-metadata']['employee_last_name'].lower()}_{payload['data-metadata']['employee_first_name'].lower()}.pdf"
    document_type = payload['template']['name']
    doc_type_prefix = ""
    match document_type:
        case "Nett Hands - Do Not Drive Agreement - 2024":
            doc_type_prefix = "do_not_drive_agreement_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "Nett Hands - Do Not Drive Agreement - 2024":
            doc_type_prefix = "do_not_drive_agreement_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "State of Illinois - Department of Revenue - Withholding Worksheet (W4)":
            doc_type_prefix = "state_w4_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "US Department of Homeland Security - Employment Eligibility Verification (I-9)":
            doc_type_prefix = "dha_i9"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "Nett Hands HCA Policy - 2024":
            doc_type_prefix = "hca_policy_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "Nett Hands & Illinois Department of Aging General Policies":
            doc_type_prefix = "idoa_agency_policies_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "Nett Hands Homehealth Care Aide (HCA)   Job Desc - 2024":
            doc_type_prefix = "job_duties_attestation"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
        case "IDPH - Health Care Worker Background Check Authorization":
            doc_type_prefix = "idph_background_check_authorization"
            filepath = os.path.join("attestations",doc_type_prefix,employee_upload_suffix )
    return filepath


def lambda_handler(event, context):
    try:
        if not isinstance(event, dict):
            docuseal_payload = json.loads(event)
        docuseal_payload = event
        response = requests.get(docuseal_payload['data']["submission"]["url"], timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(file_name, "wb") as file:
                file.write(response.content)
                with pymupdf.open(file) as doc:
                    doc.save(file_name, linear=True)
                    if upload_file_to_s3(file_name=generate_filename(docuseal_payload)):
                        return {"status": f"Uploaded to S3: {file_name}"}
    except Exception as e:
        return {"content":f"Unable to Save Document to S3: {e}", "status":422}
