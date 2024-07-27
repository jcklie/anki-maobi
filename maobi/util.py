import sys


def error(msg: str):
    """Raises an error with message `msg`. This will cause a popup in Anki."""
    sys.stderr.write(msg)
    sys.stderr.write("\n")


def debug(config, msg: str):
    """Raises an error with message `msg` if debug is enabled. This will cause a popup in Anki."""
    if config.debug:
        sys.stderr.write(msg)
        sys.stderr.write("\n")
