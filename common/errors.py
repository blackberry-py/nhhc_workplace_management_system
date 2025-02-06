from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django_require_login.mixins import public
from loguru import logger


# SECTION - Sitewide Error Handlers
@public
def maintenance_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle bad requests by logging the exception and rendering a 400.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """

    return render(request, "common/503.html", status=503)


@public
def bad_request_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle bad requests by logging the exception and rendering a 400.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """

    logger.warning(f"BAD REQUEST: {exception}")
    return render(request, "common/400.html", status=400)


@public
def permission_denied_handler(request: HttpRequest, reason=None) -> HttpResponse:
    """
    Handle forbidden requests by logging the exception and rendering a 403.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """
    logger.error(f"FORBIDDEN ERROR: {reason}")
    return render(request, "common/403_csrf.html", status=403)


@public
def page_not_found_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle requests where the route is not found by logging the exception and rendering a 404.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 404 and the 404.html template rendered.
    """
    logger.warning(f"PAGE NOT FOUND ERROR: {exception}")
    return render(request, "common/404.html", status=404)


@public
def server_error_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle requests that result in server errors by logging the exception and rendering a 500.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """
    logger.error(f"SERVER ERROR: {exception}")
    return render(request, "common/500.html", status=500)


class ElectronicMailTransmissionError(RuntimeError):
    pass
