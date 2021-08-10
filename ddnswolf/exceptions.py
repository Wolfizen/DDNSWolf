"""
Custom exception classes for use within DDNSWolf software.
The general pattern is to use these when either there is not a built-in exception that
can represent the situation (like NameError or ValueError etc.), or when an exception is
caught and then re-raised with a more informative message.

Use case 1 - Raise exception for common situation
    Example: a method in an abstract class is not implemented.

    The preferred behavior here is actually to not use a custom exception, and instead
    use the provided library exception that best fits the situation.

    Solution for Example:
        raise NotImplementedError(f"Unimplemented function in {type(self).__name__}")

Use case 2 - Raise exception for uncommon situation
    Example: A setting in a config file has an improper value.

    For these situations where a library exception isn't suitable, use the custom
    exceptions from this module. Pick the one that best matches the cause of the error.

    Solution for Example:
        raise DDNSWolfUserError(f"Config option {key} must be one of: {valid_options}")

Use case 3 - Catch exception from library and change the message
    Example: An API from a DDNSUpdater raised an exception.

    The custom exceptions in this module should be used whenever an exception is
    destined to be re-raised back to the user for notification. Pick the appropriate
    exception for the situation, and raise it along with the original caught exception
    for context.

    Solution for Example:
            ...
        catch Exception as ex:
            raise
                DDNSWolfProgramException("Unable to contact API service for CloudFlare")
            from ex
"""
from logging import Logger


def log_exception(logger: Logger, exception: BaseException):
    """
    Log an exception to the provided logger. Special handling rules for DDNSWolf custom
    exceptions will be applied.
    """
    if isinstance(exception, DDNSWolfUserException):
        logger.error(str(exception))
    else:
        logger.error(str(exception), exc_info=exception)


class DDNSWolfUserException(Exception):
    """
    An exception arising from user error or wrong input. This exception SHOULD NOT print
    a stack trace, rather print only the provided message.
    """

    pass


class DDNSWolfProgramException(Exception):
    """
    An exception arising from a program error or unexpected program state. This
    exception SHOULD print a stack trace along with its message.
    """

    pass
