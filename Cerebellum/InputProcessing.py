"""
InputProcessing.py
This file implements a filter on stdin for the test subprocess. If the message
"STOP" is received on stdin (sent by the Stop Test button in RunTestGUI), the
stop_event flag is set, which will abort the test before the next event runs.
Any other message is placed on a FIFO queue for the program to receive as usual,
using get_input() to access the queue in place of input().
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
