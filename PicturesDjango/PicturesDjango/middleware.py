from django.conf import settings


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