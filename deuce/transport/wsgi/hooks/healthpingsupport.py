"""
"""
from functools import wraps


def healthpingcheck(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if args[0].relative_uri == '/v1.0/health' \
                or args[0].relative_uri == '/v1.0/ping':
            return
        else:
            func(*args, **kwargs)
    return wrap
