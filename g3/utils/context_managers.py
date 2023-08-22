from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull


@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(devnull, "w") as f:
        with redirect_stderr(f) as err, redirect_stdout(f) as out:
            yield err, out
