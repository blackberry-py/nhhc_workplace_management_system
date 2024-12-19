from time import time

from prometheus_client import Histogram, start_http_server


class MetricsRecorder:
    def __init__(self, name, description, port=8000):
        # Initialize the Histogram metric
        self.histogram = Histogram(name, description)
        # Start the Prometheus HTTP server to expose metrics
        start_http_server(port)

    def record_operation_duration(self, operation, ctx=None):
        t1 = time()
        operation(ctx)
        dur = time() - t1
        self.histogram.observe(dur)


# Example operation
def example_operation(ctx):
    # Your operation logic here
    pass
