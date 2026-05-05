"""
Placeholder
"""

# Prevents TypeError on type hints for Python 3.8 and 3.9
from __future__ import annotations

import logging
from contextlib import contextmanager

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
