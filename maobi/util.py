import sys


class MaobiException(Exception):
    def __init__(self, message):
        super(MaobiException, self).__init__(message)


def error(msg: str):
    """ Raises an error with message `msg`. This will cause a popup in Anki. """
    sys.stderr.write(msg)
    sys.stderr.write("\n")


def debug(config, msg: str):
    """ Raises an error with message `msg` if debug is enabled. This will cause a popup in Anki. """
    if config.debug:
        sys.stderr.write(msg)
        sys.stderr.write("\n")


def _build_error_message(html: str, message: str) -> str:
    """ Constructs the HTML for an error text with message `message` over the original html. """
    return f"""<p style="text-align: center; color: red; font-size: large;">
Maobi encountered an error: <br />
{message}
</p>
{html}
"""