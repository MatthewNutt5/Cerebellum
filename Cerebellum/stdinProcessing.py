"""
Placeholder
"""

import sys, threading, queue

# Threading event to listen for STOP on stdin
# Queue to send other messages to input
stop_event = threading.Event()
input_queue = queue.Queue()

def stdin_listener():
    for line in sys.stdin:
        line = line.strip()
        if line == "STOP":
            stop_event.set()
        else:
            input_queue.put(line)

def get_input(prompt=""):
    print(prompt, end="", flush=True)
    return input_queue.get()