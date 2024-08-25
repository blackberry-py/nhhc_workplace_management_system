from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)

FAILED_SUBMISSIONS: Counter = Counter(name="failed_submissions", documentation="Metric Counter for the Number of Failed Submission attempts that failed validation", namespace="nhhc_web")
INVALID_APPLICATIONS: Counter = Counter(name="invalid_applications", documentation="Metric Counter for the Number of Failed Employment Application Submissions", namespace="nhhc_web")
S3_UPLOAD = Histogram(name="s3_upload_duration_seconds", documentation="Metric of the Duration of S3 upload of Compliance Documents from the application's /tmp to AWS S3 block storage.", unit="seconds", namespace="nhhc_compliance")
DOCUSEAL_DOWNLOAD = Histogram(name="docuseal_download_duration_seconds", documentation="Metric of the Duration of downloading singed  Compliance Documents from the DocSeal External Signing Service to /tmp storage.", unit="seconds", namespace="nhhc_compliance")

def registry_to_text():
    return generate_latest(registry)