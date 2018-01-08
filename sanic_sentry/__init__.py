# pylint:disable=too-few-public-methods,import-error

import sys
import raven
from sanic.handlers import ErrorHandler
from sanic import exceptions as sanic_exceptions


class SanicSentryErrorHandler(ErrorHandler):
    DEFAULT_EXCEPTIONS_TO_IGNORE = (sanic_exceptions.NotFound,)

    def __init__(self, dsn, exceptions_to_ignore=None):
        super(SanicSentryErrorHandler, self).__init__()
        self.exceptions_to_ignore = tuple(exceptions_to_ignore) if exceptions_to_ignore is not None else self.DEFAULT_EXCEPTIONS_TO_IGNORE
        self.sentry_client = raven.Client(dsn)

    def default(self, request, exception):
        if isinstance(exception, self.exceptions_to_ignore):
            return super(SanicSentryErrorHandler, self).default(request, exception)

        exc_info = sys.exc_info()
        self.sentry_client.captureException(
            exc_info,
            extra=dict(
                url=request.url,
                method=request.method,
                headers=request.headers,
                body=request.body,
                query_string=request.query_string
            )
        )

        return super(SanicSentryErrorHandler, self).default(request, exception)
