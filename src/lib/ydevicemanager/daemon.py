#! /usr/bin/env python
#coding=utf-8

# Ylmf Device Manager(ydm).
# Copyright (C) 2011 YLMF, Inc.
# hechao <hechao@115.com>, 2011.

__author__="hechao"
__date__ ="$2011-9-6 16:47:50$"

import dbus
import os
import re
import gobject
import logging
import hashlib
import commands
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
from dbuscall import check_polkit

if not os.path.isdir(TARGET_DIR):
    os.system("mkdir -p %s" %TARGET_DIR)

class YDeviceManager(dbus.service.Object):

    def __init__(self, loop):
        
        logging.basicConfig(level=logging.DEBUG, filename='/tmp/ydm.log',
        format='%(asctime)s %(levelname)-8s %(message)s')

        self.loop = loop
        bus_name = dbus.service.BusName(DBUS_IFACE, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)

    @dbus.service.method(DBUS_IFACE, in_signature='s', out_signature='is')
    def cmd_down(self, env_string=''):
        '''cmd down'''
        self.url = self.open_conf()
        logging.info("Download address: %s" %self.url)

        env = eval(env_string)
        if not env.get('DISPLAY'):
            cmd = "curl --connect-timeout 10 --retry 2 -4 %s/driver.xml.tar.bz2 -o %s/driver.xml.tar.bz2" %(self.url, TARGET_DIR)
            (status,output) = commands.getstatusoutput(cmd)
            logging.debug(str(output))
        else:
            cmd = "%s/terminal.py curl --connect-timeout 10 --retry 2 -4 %s/driver.xml.tar.bz2 -o %s/driver.xml.tar.bz2" %(RUN_DIR, self.url, TARGET_DIR)
            process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env)
            status = process.wait()

        logging.info("Exit status：%d" %status)

        if status:
            logging.error("Download driver list failed!")
            return C_Errno, "Network connection error, check your network!"
        else:
            return self.check_file("%s/driver.xml.tar.bz2" %TARGET_DIR)
            
    @dbus.service.method(DBUS_IFACE, in_signature='', out_signature='is')
    def ui_down(self):
        '''ui down'''
        self.url = self.open_conf()
        logging.info("Download address: %s/driver.xml.tar.bz2" %self.url)

        cmd = "curl --connect-timeout 10 --retry 2 -4 %s/driver.xml.tar.bz2 -o %s/driver.xml.tar.bz2" %(self.url, TARGET_DIR)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        status = process.wait()

        if status:
            logging.error("Download driver list failed!")
            return C_Errno, "Network connection error, check your network!"
        else:
            return self.check_file("%s/driver.xml.tar.bz2" %TARGET_DIR)

    def check_file(self, tar_file):
        '''check file'''
        hash_new = hashlib.sha1()
        with open(tar_file, 'rb') as fp:
            while True:
                data = fp.read() 
                if not data:
                    break
                hash_new.update(data)
        hash_value = hash_new.hexdigest()
        logging.info("New sha1 value：%s" %hash_value)

        cmd = "curl --connect-timeout 10 --retry 2 -4 %s/driver.xml.tar.bz2.sha1sum" %self.url
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        status = process.wait()

        if status:
            logging.error("Download driver list failed!")
            return C_Errno, "Network connection error, check your network!"
        else:
            sha1sum = process.stdout.read().split()[0]
        logging.info("Old sha1 value：%s" %sha1sum)
        
        if hash_value == sha1sum:
            os.system("tar -jxf %s -C %s" %(tar_file, TARGET_DIR))
            return 0, "%s/driver.xml" %TARGET_DIR
        else:
            logging.error("Download the file in question")
            #return P_Errno, "File checksum error!"
            '''test'''
            cmd = "curl --connect-timeout 10 --retry 2 -4 %s/driver.xml -o %s/driver.xml" %(self.url, TARGET_DIR)
            process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            return 0, "%s/driver.xml" %TARGET_DIR

    def open_conf(self):
        '''open config file'''
        try:
            with open(CONFIG, "r") as fp:
                data = fp.read()
            
            for line in data.split('\n'):
                path = re.match("YPPATH_URI=\"(.*)\"",line)
                if path:
                    return path.group(1)
        except:
            return "http://pkg.ylmf.com/packages"
    
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

    @dbus.service.method(DBUS_IFACE, in_signature='', out_signature='')
    def scan_device(self):
        '''DBus-->Python-->C++'''
        hw = lshw.lshw()
	hw.scan_device()
        
	data = hw.get_xml()
	with open(HW_XML,"w") as fp:
            fp.write(data)

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
