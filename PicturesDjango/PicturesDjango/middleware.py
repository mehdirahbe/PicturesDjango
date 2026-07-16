from django.conf import settings

from PicturesDjango.writable_access import (
    is_readonly_safe_post,
    is_writable_request,
    readonly_post_forbidden_response,
    reject_readonly_admin,
)

_MUTATING_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})


class ReadOnlyRemoteMiddleware:
    """Block DB-changing requests unless the client uses a writable host (127.0.0.1)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        denied = reject_readonly_admin(request)
        if denied is not None:
            return denied

        if (
            request.method in _MUTATING_METHODS
            and not is_writable_request(request)
            and not is_readonly_safe_post(request)
        ):
            return readonly_post_forbidden_response(request)
        return self.get_response(request)


class ShortHtmlCacheMiddleware:
    """Add a short browser cache TTL on HTML pages (GET/HEAD, 200)."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_age = getattr(settings, 'HTML_PAGE_CACHE_SECONDS', 30)

    def __call__(self, request):
        response = self.get_response(request)

        if self.max_age <= 0:
            return response

        content_type = response.get('Content-Type', '')
        if (
            request.method in ('GET', 'HEAD')
            and response.status_code == 200
            and content_type.startswith('text/html')
            and 'Cache-Control' not in response
        ):
            response['Cache-Control'] = f'max-age={self.max_age}, private'

        return response