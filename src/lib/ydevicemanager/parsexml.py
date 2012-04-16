#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gc
import re
from xml.parsers import expat

class Parser:

    def __init__(self):

        self.ver = None
        self.des = None

        self.pcid = {}
        self.part = re.compile('(.+)\((.+)\)')

        self._parser = expat.ParserCreate()
        #default size 2048
        self._parser.buffer_size = 102400
        self._parser.StartElementHandler = self.start
        self._parser.CharacterDataHandler = self.data

        self._parser.returns_unicode = False

    def start(self, tag, attrs):
        self.flag = tag
        if "name" in attrs:
            self.pkg = attrs["name"]

    def data(self, data):

        if(data == '\n'):
            return
        if(data.isspace()):
            return

        if self.flag == "version":
            self.ver = data.strip()
        elif self.flag == "description":
            self.des = data.strip()
        elif self.flag == "modaliases":
            m = data.strip()
            value = self.part.match(m)
            if not value:
                return
            module, pci = value.group(1), value.group(2)
            for alias in pci.split(','):
                self.pcid.setdefault((self.pkg, self.ver, self.des), {}).setdefault(module, []).append(alias.strip())

    def feed(self, path):
        with open(path) as fp:
            self._parser.ParseFile(fp)

    def close(self):
        del self._parser
        gc.collect()
        
