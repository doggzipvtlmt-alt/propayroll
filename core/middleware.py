import logging
import uuid

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as exc:
            logger.exception('Unhandled error: %s', exc)
            response = JsonResponse(
                {
                    'error': 'Internal server error',
                    'request_id': getattr(request, 'request_id', None),
                },
                status=500,
            )
        return response
