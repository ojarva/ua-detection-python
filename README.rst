Browser user-agent detection
============================

This library parses browser user-agent strings with data from [user-agent-string.info](http://user-agent-string.info/).

This library is loosely based on the work by Hicro Kee (hicrokee AT gmail DOT com) and Michal Molhanec (http://molhanec.net).

Usage:

::

  from uaparser import UA, UAParser
  parser = UAParser()
  parser.update_data()
  ua = UA(parser, user_agent_string)
  print ua.is_robot() # returns empty dictionary if robot is not detected
  print ua.get_browser_details() # returns empty dictionary, or browser details
  print ua.get_device_type() # returns dict containing device type fields
  print ua.get_os_details()
  # Or alternatively,
  print ua.parse() # returns all parsed fields for the UA string

Django integration
------------------

As running a large number of regexes takes a long time, Django integration uses caching.

Usage:

::

  from uaparser.django.caching_ua_parser import parse_user_agent
  parsed = parse_user_agent(request.META.get("HTTP_USER_AGENT"))

``parse_user_agent`` fetches all user-agent fields (i.e it calls ``ua.parse()``).

Settings:

- ``UA_CACHE_DIRECTORY``: directory for data file ("cache.pickle"). Mandatory.
- ``UA_CACHE_NAME``: defaults to "default". Defines custom Django cache name.
- ``UA_CACHE_PREFIX``: defaults to "parse_ua". Key prefix for cache.
- ``UA_CACHE_TIMEOUT``: defaults to 48 hours. Cache key timeout in seconds.

Middleware: add ``uaparser.django.middleware.UAParserMiddleware`` to ``MIDDLEWARE_CLASSES``.

Context processor: to add ``parsed_ua`` variable to context, add ``uaparser.django.context_processor.add_parsed_ua`` to ``CONTEXT_PROCESSORS``. This does nothing if ``UAParserMiddleware`` is not enabled.


License
-------

Licensed under the MIT license.

Copyright (c) 2014 Olli Jarva <olli@jarva.fi>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
