from django.conf import settings
from django.core.cache import get_cache
from uaparser import UA, UAParser

try:
    cache = get_cache(settings.UA_CACHE_NAME)
except AttributeError:
    cache = get_cache("default")

parser = UAParser(settings.UA_CACHE_DIRECTORY)

try:
    CACHE_PREFIX = settings.UA_CACHE_PREFIX
except AttributeError:
    CACHE_PREFIX = "parse_ua"

try:
    CACHE_TIMEOUT = settings.UA_CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 3600 * 48

__all__ = ["parse_user_agent"]

def parse_user_agent(ua):
    parsed = cache.get("%s-%s" % (CACHE_PREFIX, ua))
    if parsed:
        return parsed
    ua_parser = UA(parser, ua)
    parsed = ua_parser.parse()
    cache.set("%s-%s" % (CACHE_PREFIX, ua), parsed, CACHE_TIMEOUT)
    return parsed
