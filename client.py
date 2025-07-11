import datetime
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import psutil
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')
LOGS_FILE_PATH = os.getenv('LOGS_FILE_PATH')

SYSTEM_METRICS_URL = API_URL + '/system-metrics'
LOGS_URL = API_URL + '/logs'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('client.log', maxBytes=10 * 1024 * 1024, backupCount=1)
logging.getLogger().addHandler(log_handler)


def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    return {
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
        'cpu_usage': cpu_usage,
        'memory_usage': memory_info.percent,
    }


def send_system_metrics(metrics):
    response = requests.post(SYSTEM_METRICS_URL, json=metrics)
    logging.info(f'{SYSTEM_METRICS_URL} {response.status_code} {response.json()}')


def get_logs(last_position=0):
    logs = []
    current_position = last_position
    with open(LOGS_FILE_PATH, 'r') as log_file:
        log_file.seek(last_position)
        lines = log_file.readlines()
        for line in lines:
            parsed_log = parse_log_line(line)
            logs.append(parsed_log)
        current_position = log_file.tell()
    return logs, current_position


def parse_log_line(line):
    parts = line.strip().split(' ', 3)
    timestamp = parts[0]
    hostname = parts[1]
    process_and_pid = parts[2]
    if '[' in process_and_pid and ']' in process_and_pid:
        process = process_and_pid.split('[')[0]
        pid = process_and_pid.split('[')[1].split(']')[0]
    else:
        process = process_and_pid.rstrip(':')
        pid = ''
    message = parts[3] if len(parts) > 3 else ''
    return {
        'timestamp': timestamp,
        'hostname': hostname,
        'process': process,
        'pid': pid,
        'message': message
    }


def send_logs(logs):
    if logs:
        response = requests.post(LOGS_URL, json=logs)
        logging.info(f'{LOGS_URL} {response.status_code} {response.json()}')


last_position = 0

while True:
    current_metrics = get_system_metrics()
    send_system_metrics(current_metrics)

    logs, last_position = get_logs(last_position)
    if logs:
        send_logs(logs)

    time.sleep(1)
