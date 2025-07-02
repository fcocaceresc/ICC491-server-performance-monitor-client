import datetime

import psutil


def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    return {
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
        'cpu_usage': cpu_usage,
        'memory_usage': memory_info.percent,
    }
