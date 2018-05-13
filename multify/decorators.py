# -*- coding:utf-8 -*-
"""
Decorators
"""
import smtplib
import time

from decorator import decorator


@decorator
def retry(fn, max_retries=5, interval=3, *args, **kwargs):
    """
    Retry decorator

    :param function fn: function to look for exceptions
    :param int max_retries: max attempts
    :param int interval: time in seconds between attempts
    :param args: function positional params
    :param kwargs: function key-pair params
    :return:
    """

    result = None
    while max_retries > 0:
        try:
            result = fn(*args, **kwargs)
        except smtplib.SMTPException:
            max_retries -= 1
            time.sleep(interval)
    return result
