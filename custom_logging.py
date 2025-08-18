import io
import logging
import queue
import sys


class GradioLogHandler(logging.Handler):
    """Custom log handler to capture logs into a thread-safe queue."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)


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


class CustomLogging:
    # -------------------------------------------------
    # LOGGING SETUP TO INTERCEPT LOG OUTPUT FOR UI
    # -------------------------------------------------

    # Main log queue for UI to consume
    _log_queue = queue.Queue()

    @staticmethod
    def get_log_queue() -> queue.Queue:
        """
        Returns the main log queue for UI to consume.
        """
        return CustomLogging._log_queue

    @staticmethod
    def setup_logging() -> logging.Logger:
        """Set up logging for the application.

        Returns:
            logging.Logger: The configured logger instance.
        """
        # Set up the log handler for application logs
        gradio_log_handler = GradioLogHandler(CustomLogging.get_log_queue())
        # gradio_log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        gradio_log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(gradio_log_handler)
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.getLogger().setLevel(logging.INFO)

        stdout_logger = logging.getLogger("STDOUT")
        stderr_logger = logging.getLogger("STDERR")
        sys.stdout = StreamToLogger(stdout_logger, logging.INFO)
        sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)

        logging.captureWarnings(True)

        logger = logging.getLogger(__name__)

        return logger
