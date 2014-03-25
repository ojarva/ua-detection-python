import caching_ua_parser


class UAParserMiddleware(object):
    def process_request(self, request):
        request.parsed_ua = parse_user_agent(request.META.get("HTTP_USER_AGENT"))
