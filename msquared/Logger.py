import inspect
import enum

class Logger(object):
    class Severity(enum.IntEnum):
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40

    def __init__(self, severity = Severity.INFO):
        """
        Logs to stdout.

        Args:
            severity (Logger.Severity): Only messages with severities greater than or equal to this will be logged.
        """
        self.severity = severity

    def _message_prefix(self, stack_level = 2):
        frame = inspect.stack()[stack_level][0]
        filename = frame.f_code.co_filename
        line = frame.f_lineno
        return f"[{filename}:{line}]"

    def log(self, message, severity, stack_level = 2):
        if severity >= self.severity:
            print(f"{self._message_prefix(stack_level)} {severity.name}: {message}")

    def debug(self, message):
        self.log(message, severity=Logger.Severity.DEBUG, stack_level=3)

    def info(self, message):
        self.log(message, severity=Logger.Severity.INFO, stack_level=3)

    def warning(self, message, ErrorType: type=None):
        self.log(message, severity=Logger.Severity.WARNING, stack_level=3)

    def error(self, message, ErrorType: type=None):
        """
        Logs an error level message, or raises an error if ErrorType is provided.

        Args:
            message (str): The message to log.
            ErrorType (type): The type of error to raise. If set to None, no error is raised.
        """
        if ErrorType:
            raise ErrorType(f"{self._message_prefix(2)} {message}")
        else:
            self.log(message, severity=Logger.Severity.ERROR, stack_level = 3)
