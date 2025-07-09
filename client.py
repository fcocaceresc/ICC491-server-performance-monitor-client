import datetime
import os
import time

import psutil
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')


def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    return {
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
        'cpu_usage': cpu_usage,
        'memory_usage': memory_info.percent,
    }


def send_system_metrics(metrics):
    requests.post(API_URL + '/system-metrics', json=metrics)


while True:
    current_metrics = get_system_metrics()
    send_system_metrics(current_metrics)
    time.sleep(1)
