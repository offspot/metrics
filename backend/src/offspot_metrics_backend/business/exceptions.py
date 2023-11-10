class TooWideUsageError(Exception):
    """Exception raised when usage range is wider than expected number of minutes"""

    pass


class WrongInputTypeError(Exception):
    """Exception raised when input received does not match expectations"""

    pass
