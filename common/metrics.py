from prometheus_client import Counter, Histogram


class NHHCMetrics:
    """Manages metrics tracking for the NHHC web application.

    This class provides a comprehensive metrics tracking system for monitoring various application events and performance indicators.
    It uses Prometheus-style counters and histograms to record submission attempts, cache interactions, and document processing metrics.

    Attributes:
        NAMESPACE (str): The base namespace for all metrics in the web application.
    """

    NAMESPACE = "web_nhhc"

    def __init__(self):
        self.failed_submission_attempts = Counter(
            "failed_submission_attempts",
            "Metric Counter for the Number of Application or Client Interest Submission attempts that failed validation",
            ["application_type"],
            namespace=self.NAMESPACE,
        )
        self.cached_queryset_hit = Counter("cached_queryset_hit", "Number of requests served by a cached Queryset", ["model"])
        self.cached_queryset_miss = Counter(
            "cached_queryset_miss",
            "Number of  requests not served by a cached Queryset",
            ["model"],
        )
        self.cached_queryset_evicted = Counter("cached_queryset_evicted", "Number of cached Querysets evicted", ["model"])
        self.s3_upload_recorder = Histogram("s3_upload_duration", "Metric of the Duration of S3 upload of Compliance Documents from the application's /tmp to AWS S3 block storage.")
        self.docuseal_download_recorder = Histogram(
            "docuseal_download_duration", "Metric of the Duration of downloading singed  Compliance Documents from the DocSeal External Signing Service to /tmp storage."
        )

    def increment_failed_submissions(self, application_type: str) -> None:
        """Increments the counter for failed submission attempts for a specific application type.

        This method tracks the number of unsuccessful form submissions, categorized by the type of application.
        It helps in monitoring and analyzing submission failure rates across different application types.

        Args:
            application_type: The type of application for which the submission failed.

        Returns:
            None
        """
        self.failed_submission_attempts.labels(application_type=application_type).inc()

    def increment_cache(self, model: str, type: str) -> None:
        """Tracks cache performance metrics for different database models.

        This method increments the appropriate counter based on the cache interaction type,
        providing insights into cache hit, miss, and eviction rates for specific models.

        Args:
            model: The name of the database model being cached.
            type: The type of cache interaction ('hit', 'miss', or 'eviction').

        Returns:
            None
        """
        if type == "hit":
            self.cached_queryset_hit.labels(model=model).inc()
        elif type == "miss":
            self.cached_queryset_miss.labels(model=model).inc()
        elif type == "eviction":
            self.cached_queryset_evicted.labels(model=model).inc()


# Create a singleton instance for global use
metrics = NHHCMetrics()
