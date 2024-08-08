from prometheus_client import Histogram, start_http_server
from time import time

class MetricsRecorder:
    def __init__(self, name, description):
        # Initialize the Histogram metric
        self.histogram = Histogram(name, description)
  

    def record_operation_duration(self, operation, ctx=None):
        t1 = time()
        operation(ctx)
        dur = time() - t1
        self.histogram.observe(dur)


