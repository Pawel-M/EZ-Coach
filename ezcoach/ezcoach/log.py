GLOBAL_VERBOSE = 1


def log(message, verbose=None, level=1):
    """
    Logs the message if the level is equal or greater than the verbose value.

    :param message: a string message
    :param verbose: the value indicating the frequency of logging
    :param level: a value indicating the verbose level needed to log the message
    """
    if verbose is None:
        verbose = GLOBAL_VERBOSE

    if verbose >= level:
        print(message)
