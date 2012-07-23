#! /usr/bin/env python
#coding=utf-8

# StartOS Device Manager(ydm).
# Copyright (C) 2011 ivali, Inc.
# hechao <hechao@ivali.com>, 2011.

__author__="hechao"
__date__ ="$2011-9-6 16:47:50$"

import dbus
import os
import gobject
import logging
import ctypes
import dbus.service
from subprocess import Popen,PIPE
from dbus.mainloop.glib import DBusGMainLoop
try:
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, 'ydaemon', 0, 0, 0)
except: pass
import lshw
from globals import *
from syscall import *
from dbuscall import check_polkit


class YDeviceManager(dbus.service.Object):

    def __init__(self, loop):
        
        logging.basicConfig(level=logging.DEBUG, filename='/tmp/ydm.log',
        format='%(asctime)s %(levelname)-8s %(message)s')

        self.loop = loop
        bus_name = dbus.service.BusName(DBUS_IFACE, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
    
    @dbus.service.method(DBUS_IFACE, in_signature='ss', out_signature='s', sender_keyword='sender')
    def install(self, pname, env_string='', sender=None):
        '''install driver package'''
        env = eval(env_string)
        '''check policykit'''
        status = check_polkit(sender)
        
        if not status:
            return "Identification of permissions failed!"

        cmd = '%s/terminal.py yget --update' %RUN_DIR
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env)
        status = process.wait()
        logging.info("Update status：%d" %status)

        cmd = '%s/terminal.py yget --install -y %s' %(RUN_DIR, pname)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env)
        status = process.wait()
        logging.info("Install status：%d" %status)

        return str(status)

    @dbus.service.method(DBUS_IFACE, in_signature='ss', out_signature='s', sender_keyword='sender')
    def uninstall(self, pname, env_string='', sender=None):
        env = eval(env_string)
        '''check policykit'''
        status = check_polkit(sender)
        if not status:
            return "Identification of permissions failed!"

        cmd = '%s/terminal.py yget --remove -y %s' %(RUN_DIR, pname)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env)
        status = process.wait()
        logging.info("Uninstall status：%d" %status)

        return str(status)

    @dbus.service.method(DBUS_IFACE, in_signature='', out_signature='')
    def modprobe(self):
        '''insmod coretemp'''
        os.system("modprobe coretemp")

    @dbus.service.method(DBUS_IFACE, in_signature='', out_signature='s')
    def scan_device(self):
        '''DBus-->Python-->C++'''
        hw = lshw.lshw()
	hw.scan_device()

	data = hw.get_xml()
        return data

    @dbus.service.signal(DBUS_IFACE)
    def changed(self, msg):
        '''no return signals'''
        pass

    @dbus.service.method(DBUS_IFACE, in_signature='', out_signature='')
    def quit_loop(self):
        self.loop.quit()

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    YDeviceManager(loop)
    loop.run()
