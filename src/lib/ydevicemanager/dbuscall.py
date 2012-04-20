#!/usr/bin/env python
#coding: utf-8

#__author__ = "hechao"
#__date__ = "$2012-2-22 13:16:58$"

import dbus
from dbus.mainloop.glib import DBusGMainLoop, threads_init
from globals import DBUS_IFACE, DBUS_PATH

def init_dbus(dbus_iface=DBUS_IFACE, dbus_path=DBUS_PATH):
    '''init dbus'''
    bus = dbus.SystemBus()
    proxy = bus.get_object(dbus_iface, dbus_path)
    return dbus.Interface(proxy, dbus_interface=dbus_iface)

def call_signal(callback):
    '''add dbus signal'''
    DBusGMainLoop(set_as_default=True)
    threads_init() #Fix bug
    bus = dbus.SystemBus()
    bus.add_signal_receiver(callback, dbus_interface=DBUS_IFACE, signal_name='changed')

def check_polkit(sender):
    '''check policykit'''
    if not sender: raise ValueError('sender == None')
    
    bus = dbus.SystemBus()
    proxy = bus.get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
    authority = dbus.Interface(proxy, dbus_interface='org.freedesktop.PolicyKit1.Authority')

    subject = ('system-bus-name', {'name' : sender})
    action_id = DBUS_IFACE
    details = {}
    flags = 1            # AllowUserInteraction flag
    cancellation_id = '' # No cancellation id
    
    (granted, _, details) = authority.CheckAuthorization(subject, action_id, details, flags, cancellation_id, timeout=600)
    return granted