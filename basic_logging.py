import logging
import queue


class BasicLogging:
    """A class to set up basic logging configuration."""

    # Main log queue for UI to consume
    _log_queue = queue.Queue()

    @staticmethod
    def get_log_queue() -> queue.Queue:
        """
        Returns the main log queue for UI to consume.
        """
        return BasicLogging._log_queue

    @staticmethod
    def setup_logging() -> logging.Logger:
        """Set up logging for the application.

        Returns:
            logging.Logger: The configured logger instance.
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s | %(name)s | %(message)s",
            handlers=[logging.StreamHandler()],
        )
        logger = logging.getLogger(__name__)
        return logger
