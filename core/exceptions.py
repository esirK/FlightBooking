from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if not response:
        # If DRF can't handle the exception,
        # we manually create a response on our own and return it to the user.
        response = Response(
            {
                'errors': exc.messages
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        return response

    handlers = {
        'ValidationError': _handle_generic_error
    }

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def _handle_generic_error(exc, context, response):
    response.data = {
        'errors': response.data
    }

    return response
