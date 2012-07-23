#!/usr/bin/env python

__author__="hechao"
__date__ ="$2011-9-15 10:50:08$"

import dbus

bus = dbus.SystemBus()
proxy = bus.get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
authority = dbus.Interface(proxy, 'org.freedesktop.PolicyKit1.Authority')

system_bus_name = bus.get_unique_name()
print system_bus_name
subject = ('system-bus-name', {'name' : system_bus_name})
action_id = 'com.startos.ydm'
details = {}
flags = 1            # AllowUserInteraction flag
cancellation_id = '' # No cancellation id

(granted, _, details) = authority.CheckAuthorization(subject, action_id, details, flags, cancellation_id, timeout = 600)

print granted, _, details
