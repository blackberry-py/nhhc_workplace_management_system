import os

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import TemplateView
from loguru import logger
from rest_framework import status
import requests


def get_status_code_for_unauthorized_or_forbidden(request: HttpRequest) -> int:
    """
    Determine the appropriate HTTP status code for unauthorized or forbidden requests.

    Utility Helper function takes in an HTTP request object and checks if the user associated with the request is authenticated.
    If the user is not authenticated, it returns HTTP status code 401 (Unauthorized). If the user is authenticated but
    does not have permission to access the requested resource, it returns HTTP status code 403 (Forbidden).

    Args:
        request (HttpRequest): An HTTP request object representing the request being processed.

    Returns:
        int: The HTTP status code to be returned based on the authentication status of the user.
    """
    return status.HTTP_403_FORBIDDEN if request.user.is_authenticated else status.HTTP_401_UNAUTHORIZED


def get_content_for_unauthorized_or_forbidden(request: HttpRequest) -> bytes:
    """
    Utility Helper function that returns a message based on the user's authentication status.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        bytes: A message indicating whether the user must be logged in or an admin to complete the request.
    """
    return bytes("You Must Be An Admin In To Complete This Request", "utf-8") if request.user.is_authenticated else bytes("You Must Be Logged In To Complete This Request", "utf-8")


class CachedTemplateView(TemplateView):
    """
    A view class that caches the rendered template for a specified amount of time.

    Attributes:
        CACHE_TTL (int): The time-to-live (TTL) for the cached template in seconds.

    Methods:
        as_view(cls, **initkwargs): Returns a cached version of the template view.
    """
    @classmethod
    def as_view(cls, **initkwargs):  # @NoSelf
        return cache_page(settings.CACHE_TTL)(super(CachedTemplateView, cls).as_view(**initkwargs))


class NeverCacheMixin(object):
    """
    A mixin class that can be used to prevent caching of a view.
    """

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        """
        Dispatch method that applies the never_cache decorator to prevent caching.
        
        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        The result of calling the dispatch method of the superclass with the provided arguments and keyword arguments.
        """
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)
# Decorator to Exponetiually Retry Certain Failures.
def exponentially_retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None) -> None:
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    Args:
        ExceptionToCheck(Exception): the exception to check. may be a tuple of exceptions to check
        tries(int): number of times to try (not retry) before giving up
        delay(int): initial delay between retries in seconds
        backoff(int): backoff multiplier e.g. value of 2 will double the delay
        logger(logger instance): logger to use. If None, print
    Returns:
        None
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck:
                    msg = "%s, Retrying in %d seconds..." % (str(ExceptionToCheck), mdelay)
                    if logger:
                        # logger.exception(msg) # would print stack trace
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def internet_connection() -> bool:
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False   