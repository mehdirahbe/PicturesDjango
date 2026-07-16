import logging

from django.conf import settings
from django.http import HttpResponseForbidden
from django.urls import Resolver404, resolve
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

_DEFAULT_WRITABLE_HOSTS = ('127.0.0.1', 'localhost')
_MUTATING_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})


def _writable_hosts():
    hosts = {host.lower() for host in getattr(settings, 'WRITABLE_HOSTS', _DEFAULT_WRITABLE_HOSTS)}
    if getattr(settings, 'TESTING', False):
        hosts.add('testserver')
    return hosts


def request_host(request):
    return request.get_host().split(':')[0].lower()


def is_writable_request(request):
    return request_host(request) in _writable_hosts()


def is_readonly_safe_post(request):
    if request.method not in _MUTATING_METHODS:
        return False
    try:
        match = resolve(request.path_info)
    except Resolver404:
        return False
    safe_names = getattr(settings, 'READONLY_SAFE_POST_URL_NAMES', frozenset())
    return match.url_name in safe_names


def readonly_post_forbidden_response(request):
    logger.warning(
        "Blocked mutating %s on read-only host %s path=%s",
        request.method,
        request.get_host(),
        request.path,
    )
    return HttpResponseForbidden(
        _("Write operations are only allowed from the local server."),
        content_type="text/plain",
    )


def reject_readonly_post(request):
    if request.method not in _MUTATING_METHODS:
        return None
    if is_writable_request(request) or is_readonly_safe_post(request):
        return None
    return readonly_post_forbidden_response(request)