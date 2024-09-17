import contextlib
import re
import hashlib
import time
from os import PathLike
import json
from collections import Counter
from django.conf import settings
from loguru import logger
# Define the regex pattern for Apache log entries
pattern = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,3})?) \| ((TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|SEVERE|FATAL))   \| nhhc\.settings:<module>:31 - ([A-Za-z0-9]+)", re.IGNORECASE)

# Example log entry


class HealtHCheck():
    def __init__(self, log_file: PathLike, formatted_log:PathLike):
        self.log_type_list = []
        self.log_type = Counter(self.log_type_list)
        self.current_hash = None
        self.log_file = log_file
    
    
    def calculate_file_hash(self):
        with open(self.log_file, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash

    def process_log(self) -> None:
    # Parse the log entry using regex
        with open(self.log_file, "r") as logs:
            for log in logs:
                if match := re.match(pattern, log):
                    date_time = match[1]
                    log_type = match[2]
                    message = match[3]
                    log_record = {
                        "date_time": date_time,
                        "log_type": log_type,
                    }
                    self.log_type_list.append(log_record)
                    with open(self.formatted_logfile, "w+") as output_log:
                        log_dict = {
                                "Date_Time": date_time,
                                "Log Type": log_type,
                                "Message": message
                                }
                        output_log.write(json.dumps(log_dict))
                else:
                    print(f"Log entry does not match the expected format: {log}")

    def detect_file_changes(self) -> None:
        last_hash = self.calculate_file_hash()
        print('Health Check has began Monitoring')
        print(self.log_type_list)
        print(self.log_type)
        while True:
            if self.current_hash is None:
                self.current_hash = self.calculate_file_hash()
            self.current_hash = self.calculate_file_hash()
            if self.current_hash != last_hash:
                with contextlib.suppress(IndexError):
                    self.process_log()
                    last_logfile = self.log_type_list[-1]
                    penultimate_log=self.log_type_list[-2]
                    for key1, value1 in last_logfile:
                        for key2, value2 in penultimate_log:
                            if key1[value1] != key2[value2]:
                                print(key1[value1])
                                print(key2[value2])
                    last_hash = self.current_hash
            time.sleep(1)