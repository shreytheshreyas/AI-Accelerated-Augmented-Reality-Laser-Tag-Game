import json
import time


def get_queue(queue):
    while True:
        output = queue.get()
        if isinstance(output, dict):
            output = json.dumps(output, indent=2)
        elif isinstance(output, tuple):
            output = f"{output[0]}., {output[1]}"
        print(output)


def put_queue(queue, data, period=4, delay=2):
    time.sleep(delay)
    for d in data:
        queue.put(d)
        time.sleep(period)


def print_logs(queue):
    while True:
        print(queue.get())
