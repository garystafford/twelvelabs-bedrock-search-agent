# Reference: https://github.com/louis-she/gradio-log/blob/master/demo/app.py

import io
import logging
from pathlib import Path
import sys


class GradioLogger:
    class CustomFormatter(logging.Formatter):

        green = "\x1b[32;20m"
        blue = "\x1b[34;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format_string = "%(asctime)s - %(levelname)s - %(message)s"

        FORMATS = {
            logging.DEBUG: blue + format_string + reset,
            logging.INFO: green + format_string + reset,
            logging.WARNING: yellow + format_string + reset,
            logging.ERROR: red + format_string + reset,
            logging.CRITICAL: bold_red + format_string + reset,
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    class StreamToLogger(io.StringIO):
        """
        Redirect a stream (stdout or stderr) to logging.
        """

        # --------- NEW: Capture stdout, stderr, and warnings ---------

        def __init__(self, logger, log_level):
            super().__init__()
            self.logger = logger
            self.log_level = log_level
            self._buffer = ""

        def write(self, buf):
            self._buffer += buf
            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                if line.strip():
                    self.logger.log(self.log_level, line)

        def flush(self):
            if self._buffer.strip():
                self.logger.log(self.log_level, self._buffer.strip())
                self._buffer = ""

    @staticmethod
    def setup_logging() -> logging.Logger:
        """Set up logging for the application.

        Returns:
            logging.Logger: The configured logger instance.
        """

        formatter = GradioLogger.CustomFormatter()

        log_file = "./log_file.txt"
        Path(log_file).touch()

        ch = logging.FileHandler(log_file)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        logger = logging.getLogger("gradio_log")
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.addHandler(ch)
        sys.stdout = GradioLogger.StreamToLogger(logger, logging.INFO)
        sys.stderr = GradioLogger.StreamToLogger(logger, logging.ERROR)

        logging.captureWarnings(True)

        return logger
