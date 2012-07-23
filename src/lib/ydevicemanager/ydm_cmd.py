#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (C) 2011 StartOS(www.startos.org) Ltd.

# This application is released under the GNU General Public License
# v3 (or, at your option, any later version). You can find the full
# text of the license under http://www.gnu.org/licenses/gpl.txt.
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.
# Thank you for using free software!
#
#(c) Whise 2010,2011 <hechao@ivali.com>
#
# StartOS Device Manager
# This is free software made available under the GNU public license.

__author__ = "hechao"
__date__ = "$2011-9-13 17:48:51$"

import os
import re
import commands
import gettext
from parsexml import Parser
from syscall import cmd_down, environ
from dbuscall import init_dbus

gettext.textdomain('ydm')
def _(s):
    if os.environ.get('TERM') == "linux":
        return s
    else:
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

class ModaliasID:
    
    def __init__(self):
    
        self.alias_cache = {} 
        
        status, output = cmd_down()
        if status:
            print _(output)
            return None
       
        p = Parser()
        p.feed(output)
        p.close()
        
        self.vendor_pattern_re = re.compile('(pci|usb):v([0-9A-F]{4,8})(?:d|p)')
        
        self.alias_cache = {}
        db = p.pcid.iteritems()
        
        for pkg, pci_map in db:
            for module, aliases in pci_map.iteritems():
                for alias in aliases:
                    vp = self.vendor_pattern_re.match(alias)
                    if vp:
                        self.alias_cache.setdefault(vp.group(1), {}).setdefault(vp.group(2), {}).setdefault(alias, []).append((module, pkg))
                    else:
                        colon = alias.find(':')
                        if colon > 0:
                            bus = alias[:colon]
                        else:
                            bus = None
                        self.alias_cache.setdefault(bus, {}).setdefault(None, {}).setdefault(alias, []).append((module, pkg))
        
        hardware = self.get_hardware()
        self.get_db_handlers(hardware)
                                            
    def _do_query(self, hwid):

        if hwid.type != 'modalias' or ':' not in hwid.id:
            return []
        result = []
        m = self.vendor_pattern_re.match(hwid.id)
        
        if m:
            bus = m.group(1)
            for a, mods in self.alias_cache.get(bus, {}).get(m.group(2), {}).iteritems():
                if mods and HardwareID('modalias', a) == hwid:
                    for (m, p) in mods:
                        did = DriverID(driver_type='kernel_module', kernel_module=m)
                        if p:
                            did.properties['package'] = p
                            did.properties['pcid'] = hwid.id
                            result.append(did)
        else:
            bus = hwid.id[:hwid.id.index(':')]

        for a, mods in self.alias_cache.get(bus, {}).get(None, {}).iteritems():
            if mods and HardwareID('modalias', a) == hwid:
                for (m, p) in mods:
                    did = DriverID(driver_type='kernel_module', kernel_module=m)
                    if p:                      
                        did.properties['package'] = p
                        result.append(did)

        return result

    def get_hardware(self):

        result = self._get_modaliases()
        return result

    def _get_modaliases(self):

        hw = set()
        for path, dirs, files in os.walk('/sys/devices'):
            modalias = None

            if 'modalias' in files:
                modalias = open(os.path.join(path, 'modalias')).read().strip()
            
            elif 'ssb' in path and 'uevent' in files:
                for l in open(os.path.join(path, 'uevent')):
                    if l.startswith('MODALIAS='):
                        modalias = l.split('=', 1)[1].strip()
                        break

            if not modalias:
                continue

            driverlink = os.path.join(path, 'driver')
            modlink = os.path.join(driverlink, 'module')
            if os.path.islink(driverlink) and not os.path.islink(modlink):
                continue

            hw.add(HardwareID('modalias', modalias))
        return hw

    def get_db_handlers(self, hardware):

        flag = False
        iface = init_dbus()

        for hwid in hardware:
            dids = self._do_query(hwid)
            if not dids:
                continue

            for did in dids:
                flag = True
                print _("There are new or updated drivers available for your hardware:\nDriver name:\t%s\nDriver packages:%s\nVersion number:\t%s\nDescription:\t%s") % (did["kernel_module"], did["package"][0], did["package"][1], did["package"][2])
                put = raw_input(_("Do you want to update or install the driver(Y/N):"))
                while put.upper() != "Y" and put.upper() != "N" and put.upper() != "YES" and put.upper() != "NO":
                    put = raw_input(_("Input error, please re-enter(Y/N):"))
                    print put.upper()
            
                if put.upper() == "Y" or put.upper() == "YES":

                    status, output = None, None
                    if not os.environ.get('DISPLAY'):
                        cmd = "sudo yget --install -y %s" % did["package"][0]
                        (status, output) = commands.getstatusoutput(cmd)
                        if status:
                            print _("Install failed：%s") % str(output)
                        else:
                            print str(output)
                    else:
                        '''set timeout is 600s, the default is 25s'''
                        iface.install(did["package"][0], environ(), timeout=600)

        iface.quit_loop()
        if not flag:
            print _("No proprietary drivers are in use on this system.")

if __name__ == '__main__':
    ModaliasID()
