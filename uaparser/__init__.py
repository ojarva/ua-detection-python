"""
A python interface for parsing web browser user-agent strings.


Uses database from http://user-agent-string.info/ .

(c) 2014 Olli Jarva <olli@jarva.fi>

Loosely based on the version by
- Hicro Kee <hicrokee AT gmail DOT com>
- Michal Molhanec http://molhanec.net

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


Usage:

::
  from uadetection import UAParser
  parser = UAParser("/path/to/cache_folder")
  parser.download_data() # Data files are not downloaded, nor updated automatically.
  result = parser.parse("User-agent string")

Field definitions: only fields that were parsed exists. Use parsed_value.get("field_name")
to check whether the data is available.

* 'type': browser type
* 'ua_family': User agent family, e.g "Chrome"
* 'ua_name': User
* 'ua_url':
* 'ua_company':
* 'ua_company_url':
* 'ua_icon':'unknown.png'
* 'ua_info_url':
* 'os_family': Operating system family, e.g "Windows"
* 'os_name': Operating system name, "Windows XP"
* 'os_url': URL to operating system site, e.g wikipedia article
* 'os_company': Name of the company manufacturing the OS
* 'os_company_url': URL to the company website
* 'os_icon': Name of the icon for OS
* 'device_type': type of the device.
* 'device_icon': 'unknown.png'
* 'device_info_url':

"""

import os
import re
import time
import urllib2

try:
    import cPickle as pickle
except ImportError:
    import pickle

__all__ = ["UAParser", "UA"]


class UA:
    def __init__(self, parser, ua):
        self.parser = parser
        self.ua = ua
        self.browser_version_info = False
        self.browser_id = False
        self.browser_type = False

    def parse(self):
        """ Returns all browser details, or empty dictionary. """
        if not self.ua:
            # If useragent evaluates as False, return empty data.
            return {}
        ret = self.is_robot()
        if ret:
            return ret
        ret = self.get_browser_details()
        if len(ret.keys()) == 0:
            return ret

        ret.update(self.get_browser_details())
        ret.update(self.get_os_details())
        ret.update(self.get_device_type())
        return ret

    def is_robot(self):
        """ Returns dictionary if the UA is robot,
            {}, if no match found. """
        parsed_data = {}
        for index in self.parser.data['robots']['order']:
            test = self.parser.data['robots'][index]
            if test[0] == self.ua:
                parsed_data['type'] = 'Robot'
                for i, keyname in enumerate(UAParser.UA_INDEX):
                    parsed_data[keyname] = test[i + 1]
                try:
                    del parsed_data[""]
                except KeyError:
                    pass
                return parsed_data
        return {}

    def get_browser_details(self):
        """ Returns True if browser is found   """
        # Is the UA valid browser?
        self.browser_id = None
        self.browser_version_info = None
        for index in self.parser.data['browser_reg']['order']:
            test = self.parser.data['browser_reg'][index]
            # .search is remarkably faster than .findall.
            # As this only matches once, performance hit of running
            # regex twice is still worth of it.
            test_rg = test[0].search(self.ua)
            if test_rg:
                test_rg = test[0].findall(self.ua)
                self.browser_id = int(test[1])
                self.browser_version_info = test_rg[0]
                break

        if self.browser_id is None:
            return {}

        self.browser_type = None
        parsed_data = {}
        if self.browser_id in self.parser.data['browser']:
            for i, keyname in enumerate(UAParser.BROWSER_INDEX):
                parsed_data[keyname] = self.parser.data["browser"][self.browser_id][i + 1]

            # Get browser type
            browser_type_id = int(self.parser.data['browser'][self.browser_id][0])
            parsed_data['type'] = self.parser.data['browser_type'][browser_type_id][0]
            self.browser_type = parsed_data["type"]
            # Exception for ua_name: combine browser info.
            # info is obtained in browser_reg search.
            parsed_data['ua_name'] = "%s %s" % (self.parser.data['browser'][self.browser_id][1], self.browser_version_info)
        return parsed_data

    def get_device_type(self):
        # Get device type
        parsed_data = {}
        for index in self.parser.data["device_reg"]["order"]:
            test = self.parser.data["device_reg"][index]
            test_rg = test[0].search(self.ua)
            if test_rg:
                device_id = int(test[1])
                if device_id in self.parser.data["device"]:
                    for i, keyname in enumerate(UAParser.DEVICE_INDEX):
                        parsed_data[keyname] = self.parser.data["device"][device_id][i]
                    return parsed_data

        # No device type found. Match it based on the type of the device.
        if not self.browser_type:
            self.get_browser_details()

        if self.browser_type in ("Other", "Library", "Validator", "Useragent Anonymizer"):
            device_number = 1
        elif self.browser_type in ("Mobile Browser", "Wap Browser"):
            device_number = 3
        else:
            device_number = 2
        for i, keyname in enumerate(UAParser.DEVICE_INDEX):
            parsed_data[keyname] = self.parser.data["device"][device_number][i]

        return parsed_data

    def get_os_details(self):
        if not self.browser_id:
            if not self.is_valid_browser():
                return {}

        parsed_data = {}
        # Get OS details. If browser information exists in browser_os,
        # don't run regex chacks for maching the OS.
        if self.browser_id in self.parser.data['browser_os']:
            os_id = int(self.parser.data['browser_os'][self.browser_id][0])
            for i, keyname in enumerate(UAParser.OS_INDEX):
                parsed_data[keyname] = self.parser.data["os"][os_id][i]
            return parsed_data

        # Try to match OS with regexps
        for index in self.parser.data['os_reg']['order']:
            test = self.parser.data['os_reg'][index]
            test_rg = test[0].search(self.ua)
            if test_rg:
                os_id = int(test[1])
                if os_id in self.parser.data['os']:
                    for i, keyname in enumerate(UAParser.OS_INDEX):
                        parsed_data[keyname] = self.parser.data["os"][os_id][i]
                    return parsed_data
        return parsed_data


class UAParser:

    INI_DOWNLOAD_URL = 'http://user-agent-string.info/rpc/get_data.php?key=free&format=ini'
    VERSION_CHECK_URL = 'http://user-agent-string.info/rpc/get_data.php?key=free&format=ini&ver=y'

    # Field names for user-agent-string.info ini file fields.
    OS_INDEX = ['os_family', 'os_name', 'os_url', 'os_company', 'os_company_url', 'os_icon']
    UA_INDEX = ['ua_family', 'ua_name', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', '', 'ua_info_url']
    BROWSER_INDEX = ['ua_family', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
    DEVICE_INDEX = ["device_type", "device_icon", "device_info_url"]

    def __init__(self, data_directory=""):
        self.data_directory = data_directory
        self.data_filename = os.path.join(self.data_directory, "cache.pickle")
        self._data = None

    @classmethod
    def to_python_regex(cls, reg):
        """ Converts generic regexp to Python re. """
        # Remove /
        reg_l = reg[1:reg.rfind('/')]
        # Get flags
        reg_r = reg[reg.rfind('/') + 1:]
        flags = 0
        if 's' in reg_r:
            flags = flags | re.S
        if 'i' in reg_r:
            flags = flags | re.I
        return re.compile(reg_l, flags)

    def parse_ini_file(self, file):
        """
        Parses an ini file into a dictionary structure
        """
        data = {}
        current_section = 'unknown'
        section_pat = re.compile(r'^\[(\S+)\]$')
        option_pat = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

        for line in file.split("\n"):
            option = option_pat.findall(line)
            if option:
                key = int(option[0][0])
                if key in data[current_section]:
                    data[current_section][key].append(option[0][1])
                else:
                    opt = option[0][1]
                    if current_section in ("browser_reg", "os_reg", "device_reg"):
                        data[current_section][key] = [UASparser.to_python_regex(opt), ]
                    else:
                        data[current_section][key] = [opt, ]
                    data[current_section]['order'].append(key)
            else:
                section = section_pat.findall(line)
                if section:
                    current_section = section[0]
                    data[current_section] = {'order': []}
        return data

    def _fetchURL(self, url):
        """
        Get remote context by a given url
        """
        resq = urllib2.Request(url)
        context = urllib2.urlopen(resq)
        return context.read()

    def update_data(self):
        """
        Check whether data is out-of-date
        """
        ver_data = None

        # Check the latest version first
        # pass if no need to update
        ver_data = self._fetchURL(self.VERSION_CHECK_URL)
        if os.path.exists(self.data_filename):
            cache_file = open(self.data_filename, 'rb')
            data = pickle.load(cache_file)
            if data['version'] == ver_data:
                self._data = data
                return True

        cache_file = open(self.data_filename, 'wb')
        ini_file = self._fetchURL(self.INI_DOWNLOAD_URL)
        ini_data = self.parse_ini_file(ini_file)
        if ver_data:
            ini_data['version'] = ver_data

        pickle.dump(ini_data, cache_file)

        return True

    @property
    def data(self):
        if not self._data:
            self._data = pickle.load(open(self.data_filename, 'rb'))
        return self._data
