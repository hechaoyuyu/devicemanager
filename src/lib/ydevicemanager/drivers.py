#! /usr/bin/python
# -*- coding:utf-8 -*-

# StartOS Device Manager(ydm).
# Copyright (C) 2011 ivali, Inc.
# hechao <hechao@ivali.com>, 2011.

__author__="hechao"
__date__ = "$2011-9-13 17:48:51$"

import gettext
import os
import re
from parsexml import Parser
from syscall import ui_down

gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)

class HardwareID:

    _recache = {}

    def __init__(self, type, id):
        self.type = type
        self.id = id

    def __repr__(self):
        return "HardwareID('%s', '%s')" % (self.type, self.id)

    def __eq__(self, other):
        if type(self) != type(other) or self.type != other.type:
            return False

        if self.type != 'modalias':
            return self.id == other.id

        if '*' in self.id:
            if '*' in other.id:
                return self.id == other.id
            else:
                return self.regex(self.id).match(other.id)
        else:
            if '*' in other.id:
                return self.regex(other.id).match(self.id)
            else:
                return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):

        if self.type == 'modalias':
            return hash(self.type) ^ hash(self.id[:self.id.find(':')])
        else:
            return hash(self.type) ^ hash(self.id)

    @classmethod
    def regex(klass, pattern):

        r = klass._recache.get(pattern)
        if not r:
            r = re.compile(re.escape(pattern).replace('\\*', '.*') + '$')
            klass._recache[pattern] = r
        return r

class DriverID:

    def __init__(self, ** properties):
        self.properties = properties

    def __getitem__(self, key):
        return self.properties.__getitem__(key)

    def __contains__(self, key):
        return self.properties.__contains__(key)

    def __setitem__(self, key, value):
        self.properties.__setitem__(key, value)

class Driver:

    def __init__(self):

        self.alias_cache = {}
        self.dri_list = {}

        self.status, self.output = ui_down()
        if self.status:
            return

        dri_xml = Parser()
        dri_xml.feed(self.output)
        dri_xml.close()

        self.vendor_pattern_re = re.compile('(pci|usb):v([0-9A-F]{4,8})(?:d|p)')
        self.key_pattern_re = re.compile('(pci|usb):v([0-9A-F]{4,8})(?:d|p)([0-9A-F]{4,8})')

        dri_db = dri_xml.pcid.iteritems()

        '''web'''
        for pkg, pci_map in dri_db:
            for module, aliases in pci_map.iteritems():
                for alias in aliases:
                    vp = self.vendor_pattern_re.match(alias)
                    if vp:
                        self.alias_cache.setdefault(vp.group(1), {}).setdefault(vp.group(2), \
                        {}).setdefault(alias, []).append((module, pkg))
        
    def packed_env_string(self):

        env = dict(os.environ)
        return repr(env)

    def get_hardware(self):

        result = self._get_modaliases()
        return result

    def _get_modaliases(self):

        '''locale'''
        hw = set()
        for path, dirs, files in os.walk('/sys/devices'):
            modalias = None

            if 'modalias' in files:
                with open(os.path.join(path, 'modalias')) as fp:
                    modalias = fp.read().strip()

            elif 'ssb' in path and 'uevent' in files:
                fp = open(os.path.join(path, 'uevent'))
                for l in fp:
                    if l.startswith('MODALIAS='):
                        modalias = l.split('=', 1)[1].strip()
                        break
                fp.close()

            if not modalias:
                continue

            driverlink = os.path.join(path, 'driver')
            modlink = os.path.join(driverlink, 'module')
            if os.path.islink(driverlink) and not os.path.islink(modlink):
                continue

            hw.add(HardwareID('modalias', modalias))
        return hw

    def _do_query(self, hwid):

        if hwid.type != 'modalias' or ':' not in hwid.id:
            return {}

        pcid = {}
        mate = self.vendor_pattern_re.match(hwid.id)

        if mate:
            vp = self.key_pattern_re.match(hwid.id)
            key = None
            if vp:
                key = vp.group(2)[-4:] + ":" + vp.group(3)[-4:]

            bus = mate.group(1) #bus type
            vid = mate.group(2) #vendor id
            
            for id, mods in self.alias_cache.get(bus, {}).get(vid, {}).iteritems():
                if mods and HardwareID('modalias', id) == hwid: #local id eq web id
                    for (mod, pkg) in mods:
                        if pkg and key:
                            pcid.setdefault(key, []).append((mod, pkg))
                        
        return pcid

    def get_drivers(self):
        
        '''get driver list'''
        hardware = self.get_hardware()
        for hwid in hardware:
            pcid = self._do_query(hwid)
            if pcid:
                self.dri_list.update(pcid)
