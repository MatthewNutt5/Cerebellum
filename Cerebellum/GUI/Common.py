"""
Placeholder
"""

import logging
from contextlib import contextmanager
from PySide6.QtWidgets import QPlainTextEdit

# Logging handler and context manager to capture all logging messages during an operation

class BufferedLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.buffer: list[str] = []

    def emit(self, record):
        self.buffer.append(self.format(record))

@contextmanager
def capture_warnings():

    handler = BufferedLogHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)

    try:
        yield handler.buffer
    finally:
        logging.getLogger().removeHandler(handler)



# Logging handler and context manager to forward logging messages to a QPlainTextEdit during an operation
# This will need to be rewritten to support multi-process execution for GUI control over a live test

class LogBoxHandler(logging.Handler):
    def __init__(self, log_box: QPlainTextEdit):
        super().__init__()
        self.log_box = log_box

    def emit(self, record):
        self.log_box.appendPlainText(self.format(record))

@contextmanager
def logging_to_box(log_box: QPlainTextEdit):

    handler = LogBoxHandler(log_box)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    
    yield
    
    logging.getLogger().removeHandler(handler)
