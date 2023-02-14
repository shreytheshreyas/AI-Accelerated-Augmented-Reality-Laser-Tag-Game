import json
import time


def get_queue(queue):
    while True:
        output = queue.get()
        if isinstance(output, object):
            output = json.dumps(output, indent=2)
        elif isinstance(output, tuple):
            a, b = output
            output = f"{a}, {b}"
        print(output)


def put_queue(queue, data, period=2, delay=2):
    time.sleep(delay)
    for d in data:
        queue.put(d)
        time.sleep(period)
