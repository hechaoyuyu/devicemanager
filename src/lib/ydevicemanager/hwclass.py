#!/usr/bin/env python
# -*- coding: utf-8 -*-

# StartOS Device Manager(ydm).
# Copyright (C) 2011 ivali, Inc.
# hechao <hechao@ivali.com>, 2011.

#__author__="hechao"
#__date__ ="$2011-12-20 16:36:20$"

import gtk
import time
import os
import pango
import re
import gobject
import gettext
from syscall import *
from globals import *
from widgets import BaseFucn

gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)

F = lambda x: "%1.f"%x if x*10 % 10 == 0 else "%1.2f"%x

class Computer(gtk.VBox, BaseFucn):

    def __init__(self, product=""):
	gtk.VBox.__init__(self)

        tmp = re.findall("\[(.*)\]", product[-11:])
        if tmp:
            self.pcid = tmp[0]
        else:self.pcid = ""

    def title_box(self, text):

	label = gtk.Label()
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" %text)

        hbox = gtk.HBox()
	hbox.pack_start(label, False)

        align = self.box_align(hbox, 10, 20)
        self.pack_start(align, False)

    def tag_box(self, text, record=None):

	label = gtk.Label()
	label.set_alignment(0, 0)
	label.set_width_chars(15)
        label.set_markup("<span foreground='#1A3E88' font_desc='10'>%s</span>" % text)

        hbox = gtk.HBox()
	hbox.pack_start(label, False)

        if record:
            self.temp = gtk.Label()
            self.temp.set_selectable(True)
            hbox.pack_start(self.temp, False)

            gobject.timeout_add(2000, self.updates, record)
            
        align = self.box_align(hbox, 8, 20)
	self.pack_start(align, False)

    def updates(self, record):
        '''refresh temperature'''
        val = ""
        if record == "cpu":
            val = cpu_sensor()
        else:
            val = disk_sensor(record)
        if not val:
            return False

        r = re.match("\d+",val)
        if r:
            if int(r.group()) >= 60:
                val = "<span color='red'>%s</span>" %val

	self.temp.set_tooltip_text(val)
	text = _("Current temperature:")
        self.temp.set_markup("<span foreground='#1A3E88' font_desc='10'>%s</span>" %(text + val))

        return True

    def body_box(self, bodys):

        for body in bodys:
            if not body[1]:
                continue

            leftlabel = gtk.Label()
            leftlabel.set_alignment(0, 0)
            leftlabel.set_width_chars(15)
            leftlabel.set_markup("<span font_desc='10'>%s</span>" %body[0])

            hbox = gtk.HBox()
            hbox.pack_start(leftlabel, False)

            self.rigthlabel = gtk.Label()
            self.rigthlabel.set_alignment(0, 0)
            self.rigthlabel.set_selectable(True)
            self.rigthlabel.set_markup("<span font_desc='10'>%s</span>" %body[1])

            length = len(body[1])
            if length >= 50:
                l = length / 50
                s = ""
                for i in range(1, l + 1):
                    s += body[1][(i-1)*50:i*50] + "\n"
                s += body[1][i*50:]
                self.rigthlabel.set_tooltip_text(s)
            else:
                self.rigthlabel.set_tooltip_text(body[1])

            hbox.pack_start(self.rigthlabel)
            align = self.box_align(hbox, 7, 20)

            ebox = gtk.EventBox()
            ebox.set_visible_window(False)
            #ebox = self.default_ebox()
            ebox.connect("size-allocate", self.label_align)
            ebox.add(align)
            self.pack_start(ebox)

    def label_align(self, widget, event):
        self.rigthlabel.set_ellipsize(pango.ELLIPSIZE_END)

    def box_align(self, widget, top, left):

	align = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        align.set_padding(top, 0, left, left)

        align.add(widget)
	return align

    def dev_logo(self, vendor="", product=""):

        icon_url = self.match_vid(vendor, product)
        if not icon_url:
            return None
	icon, url, name = icon_url
	button = self.ebox_button()
	button.connect('button-press-event', self.click_on, url)

        vbox = gtk.VBox()

	label = gtk.Label()
        label.set_markup("<span foreground='#1A3E88' font_desc='10'>%s</span>" % _(name))
        image = gtk.image_new_from_file(LOGO + icon)

        vbox.pack_start(image, False)
	vbox.pack_start(label, False, False, 8)
        button.add(vbox)

	align = self.box_align(button, 10, 50)
	return align

    def match_vid(self, v, p=""):

        def get_url(v, p):
            '''vendors'''
            v = v.split(" ")[0]
            tmp = re.findall("([a-zA-Z0-9-]+)", v)
            if tmp:
                url = VENDORS.get(tmp[0].upper())
                if url:
                    return url
                else:
                    p = p.split(" ")[0]
                    url = VENDORS.get(p.upper())
                    if url:
                        return url
            else:
                p = p.split(" ")[0]
                url = VENDORS.get(p.upper())
                if url:
                    return url
        
        tmp = re.findall("\[(.*)\]", v[-6:])
        if tmp:
            '''ID'''
            url = VENDORS.get(tmp[0])
            if url:
                return url
            else:
                return get_url(v, p)
        else:
            return get_url(v, p)

    def click_on(self, widget, event, url):
	os.system("xdg-open http://%s &" % url)

class System(Computer):

    category = "system"

    def __init__(self, description, product, vendor, version, serial, width, config, capability):
        Computer.__init__(self, product)

        if not description:
            return 

	self.title_box(_("Computer preview"))
	self.tag_box(_("Basic Info"))

        bodys = []
        bodys.append((_("CDescription"), description))
        bodys.append((_("CProduct"), product))
        bodys.append((_("Vendor"), vendor))
        bodys.append((_("Serial"), serial))
        bodys.append((_("UUID"), config.get("uuid")))
        self.body_box(bodys)

	self.tag_box(_("System Info"))

        del bodys[:]
        bodys.append((_("Hostname"), host_name()))
        bodys.append((_("Username"), user()))

	up_time = uptime()
	day = up_time.get("day")
	runtime = ""
	if day:
	    runtime = day + _("day")
	hour = up_time.get("hour")
	if hour:
	    runtime += hour + _("hour")
	minute = up_time.get("minute")
	if minute:
	    runtime += minute + _("minute")
        bodys.append((_("Runtime"), runtime))
        bodys.append((_("System version"), os_version()[1]+' '+os_version()[2]))
        bodys.append((_("Install time"), install_time()))

	release, machine = kernel()
        bodys.append((_("Kernel version"), release))
        bodys.append((_("Kernel arch"), machine))

        bodys.append((_("Xorg version"), xorg()))

	glinfo = opengl()
	if glinfo:
	    bodys.append((_("Rendering"), glinfo[0]))
            bodys.append((_("OpenGL version"), glinfo[2]))
	    bodys.append((_("OpenGL renderer"), glinfo[1]))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Motherboard(Computer):

    category = "motherboard"

    def __init__(self, description, product, vendor, version, serial):
        Computer.__init__(self, product)

	self.title_box(_(self.category) + _("Info"))
        self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("MProduct"), product))
	bodys.append((_("MVendor"), vendor))
        bodys.append((_("Serial"), serial))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Bios(Computer):

    category = "bios"

    def __init__(self, description, product, vendor, version, date, size, capability):
        Computer.__init__(self, product)

	self.tag_box("BIOS" + _("Info"))

        bodys = []
	bodys.append((_("BVendor"), vendor))
	bodys.append((_("BVersion"), version))

	try:
	    date = time.strptime(date,"%m/%d/%Y")
	    date = time.strftime("%Y-%m-%d", date)
	except:pass
	bodys.append((_("Date"), date))

	text = ",".join(capability)
	bodys.append((_("BCapability"), text))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Cpu(Computer):

    category = "cpu"

    def __init__(self, description, product, vendor, version, businfo, serial, slot, size, capacity, width, clock, config, capability):
        Computer.__init__(self, product)

	self.title_box(_(self.category) + _("Info"))
	self.tag_box(_("Basic Info"), "cpu")

        bodys = []
        bodys.append((_("cpu"), product))
        bodys.append((_("Vendor"), vendor))

        if size:
            size = str(int(size) / 1000000) + "MHz"
            bodys.append((_("Current Hz"), size))

        if clock:
            clock = str(int(clock) / 1000000) + "MHz"
            bodys.append((_("FSB"), clock))

        if capacity:
	    maxsize = str(int(capacity) / 1000000) + "MHz"
	    bodys.append((_("Max Hz"), maxsize))
        self.body_box(bodys)

	self.tag_box(_("Core Info"))

        del bodys[:]
	bodys.append((_("Version"), version))

	threads = cpuinfo()
        cpunums = config.get("cores")
        if cpunums:
            cpunums = cpunums + _("core") + "/" + threads + _("thread")
            bodys.append((_("Core Num"), cpunums))

        bodys.append((_("Slot"), slot))

        if width:
            bodys.append((_("Width"), width + _("bit")))

        bodys.append((_("Serial"), serial))

	text = ",".join(capability)
	bodys.append((_("Order"), text))
        self.body_box(bodys)

        self.logo = self.dev_logo(vendor, product)

        self.tag_box(_("Cache Info"))


class Cache(Computer):

    category = "cache"

    def __init__(self, description, product, vendor, version, slot, size):
        Computer.__init__(self, product)

        bodys = []
        if size:
            size = str(int(size) / 1024) + "KB"
            bodys.append((_(description), size))
            self.body_box(bodys)

class Memory(Computer):

    category = "memory"

    def __init__(self, description, product, vendor, version, slot, size):
        Computer.__init__(self, product)

        if description == "RAM memory":
            return

	self.title_box(_(self.category) + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("MDescription"), _(description)))

        if size:
            size = F(float(size) / 1024**3) + "GB"
            bodys.append((_("Size"), size))
        self.body_box(bodys)

class Bank(Computer):

    category = "bank"

    def __init__(self, description, product, vendor, version, serial, slot, size, width, clock):
        Computer.__init__(self, product)

	self.tag_box(_("Physical Memory"))

        bodys = []
	bodys.append((slot, description))
        bodys.append((_("Memory product"), product))
        bodys.append((_("Vendor"), _(vendor)))
        
        if size:
            size = F(float(size) / 1024**3) + "GB"
            bodys.append((_("Memory size"), size))

	if width:
            bodys.append((_("Width"), width + _("bit")))

        bodys.append((_("Serial"), serial))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Display(Computer):

    category = "display"

    def __init__(self, description, product, vendor, version, businfo, config, capability):
        Computer.__init__(self, product)

        try:
            ID = re.findall("\[(.*)\]", vendor[-6:])[0]
        except:ID = "8086"
	if ID == "1002" or ID == "10DE":
	    cardtype = _("Graphics card")
	else:
	    cardtype = _("Integrated graphics")

	self.title_box(cardtype + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("Display card"), product))
        bodys.append((_("Vendor"), vendor))
        bodys.append((_("Bus addr"), businfo))
        self.body_box(bodys)

	self.tag_box((_("Expand Info")))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Display driver"), config.get("driver")))

	text = ",".join(capability)
	bodys.append((_("Display cap"), text))
	self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Monitor(Computer):

    category = "monitor"

    def __init__(self, description, product, vendor, version):
	Computer.__init__(self, product)

	dict = get_monitor()

	self.title_box(_(self.category) + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
	product = dict.get("product")
        if product:
            bodys.append((_(self.category), product.upper()))

	vendor = dict.get("vendor", '')
	bodys.append((_("Vendor"), _(vendor)))

	year = dict.get("year")
	week = dict.get("week")
	if year and week:
            bodys.append((_("Make time"), _("%s year num %s week") %(year,week)))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Apparent Area"), dict.get("size")))

        inch = dict.get("in")
        if inch:
            bodys.append((_("Dimension"), inch + _("inches")))

        ratio = get_ratio()
        if ratio:
            bodys.append((_("Current resolution"), ratio))

	bodys.append((_("Max resolution"), dict.get("maxmode")))
	bodys.append((_("Gamma"), dict.get("gamma")))
	bodys.append((_("Current output"), dict.get("output")))

	support = dict.get("support output")
	if support:
            text = ",".join(support)
            bodys.append((_("Support output"), text))

	bodys.append((_("Current chip"), dict.get("chip")))
        self.body_box(bodys)

        self.logo = self.dev_logo(vendor)

class Modem(Computer):

    category = "generic"

    def __init__(self, description, product, vendor, version, businfo, serial, config, capability):
        Computer.__init__(self, product)

	if description:
            self.title_box(_(description))
        else:
            self.title_box(_(self.category))
        self.tag_box(_("Basic Info"))

        bodys = []
        if product:
            bodys.append((_("Name"), product))
        else:
            bodys.append((_("Name"), description))

	bodys.append((_("Vendor"), vendor))
	bodys.append((_("Bus addr"), businfo))
        bodys.append((_("Serial"), serial))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Driver"), config.get("driver")))
	bodys.append((_("Max power"), config.get("maxpower")))
	bodys.append((_("Speed"), config.get("speed")))

	text = ",".join(capability)
	bodys.append((_("Capability"), text))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Multimedia(Computer):

    category = "multimedia"

    def __init__(self, description, product, vendor, version, businfo, config, capability):
        Computer.__init__(self, product)

	if description:
	    self.title_box(_(description) + _("Info"))
	else:
	    self.title_box(_("Audio device") + _("Info"))

	self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("Name"), product))
        bodys.append((_("Vendor"), vendor))
        bodys.append((_("Bus addr"), businfo))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Driver"), config.get("driver")))
	bodys.append((_("Max power"), config.get("maxpower")))
	bodys.append((_("Speed"), config.get("speed")))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Network(Computer):

    category = "network"

    def __init__(self, description, product, vendor, version, businfo, logicalname, serial, capacity, config, capability):
        Computer.__init__(self, product)

        if description != "Ethernet interface" and description != "Wireless interface":
            return

	nettype = description.split(" ")[0]
	self.title_box(_(nettype) + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
        bodys.append((_("Network name"), product))
        bodys.append((_("Vendor"), vendor))
        bodys.append((_("Bus addr"), businfo))
	bodys.append((_("Logicalname"), logicalname))
        bodys.append((_("MAC addr"), serial.upper()))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
        bodys.append((_("Firmware"), version))

	if capacity:
	    maxwidth = str(int(capacity) / 1000000) + "Mbps"
	    bodys.append((_("Max width"), maxwidth))

        bodys.append((_("Network driver"), config.get("driver")))
        bodys.append((_("Driver ver"), config.get("driverversion")))
	bodys.append((_("IP addr"), config.get("ip")))
	bodys.append((_("Link"), config.get("link", _("Empty"))))
	bodys.append((_("Wireless spec"), config.get("wireless")))

	text = ",".join(capability)
	bodys.append((_("Network cap"), text))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Disk(Computer):

    category = "disk"

    def __init__(self, description, product, vendor, version, businfo, logicalname, serial, size, config, capability):
        Computer.__init__(self, product)

	self.title_box(_(description) + _("Info"))

	if description == "ATA Disk":
	    dict = udisks(logicalname)

	    self.tag_box(_("Basic Info"), logicalname)#dict.get("temp"))

            bodys = []
	    bodys.append((_("DProduct"), _(vendor) + " " + product))

            if size:
                size = str(int(size) / 1000**3) + "GB"
                bodys.append((_("DCapacity"), size))

	    bodys.append((_("Rotate speed"), dict.get("rota")))
            bodys.append((_("Bus addr"), businfo))
            bodys.append((_("Logicalname"), logicalname))
            bodys.append((_("Serial"), serial))
            self.body_box(bodys)

	    self.tag_box(_("S.M.A.R.T"))

            del bodys[:]
	    bodys.append((_("Last time"), dict.get("boot")))

	    sumtime = dict.get("sumtime")
	    sumnub = dict.get("sumnub")
	    if sumnub and sumtime:
		bodys.append((_("Use"), _("Sum use %s,total %s") %(sumnub, sumtime)))

	    bodys.append((_("Err sector num"), dict.get("unsect")))
	    bodys.append((_("Disk status"), _(dict.get("state"))))
            bodys.append((_("Firmware"), version))

	    wwn = dict.get("wwn")
	    if wwn:
		bodys.append((_("WWN"), wwn.upper()))
            self.body_box(bodys)

	    self.logo = self.dev_logo(vendor, product)

	else:
	    self.tag_box(_("Basic Info"))

            bodys = []
            if size:
                size = F(float(size) / 1000**3) + "GB"
                bodys.append((_("Capacity"), size))

	    bodys.append((_("Bus addr"), businfo))
	    bodys.append((_("Logicalname"), logicalname))
            self.body_box(bodys)

class Storage(Computer):

    category = "storage"

    def __init__(self, description, product, vendor, version, businfo, logicalname, serial, config, capability):
        Computer.__init__(self, product)

	if description:
	    self.title_box(_(description) + _("Info"))
	else:
	    self.title_box(_(self.category) + _("Info"))

	self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("Name"), product))
	bodys.append((_("Vendor"), vendor))
        bodys.append((_("Serial"), serial))
        bodys.append((_("Bus addr"), businfo))
        bodys.append((_("Logicalname"), logicalname))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Driver"), config.get("driver")))
	bodys.append((_("Max power"), config.get("maxpower")))
	bodys.append((_("Speed"), config.get("speed")))

	text = ",".join(capability)
	bodys.append((_("Capability"), text))
        self.body_box(bodys)
        
	self.logo = self.dev_logo(vendor)

class Cdrom(Computer):

    category = "cdrom"

    def __init__(self, description, product, vendor, version, businfo, logicalname, config, capability):
        Computer.__init__(self, product)

	self.title_box(_(self.category) + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
        bodys.append((_("Cdrom name"), product))
        bodys.append((_("Vendor"), vendor))
        bodys.append((_("Bus addr"), businfo))
	bodys.append((_("Logicalname"), logicalname))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
        bodys.append((_("Firmware"), version))

	status = config.get("status")
	bodys.append((_("Dev status"), _(status)))

	text = ",".join(capability)
	bodys.append((_("Cdrom cap"), text))
	self.body_box(bodys)
        
	self.logo = self.dev_logo(vendor)

class Imput(Computer):

    category = "input"

    def __init__(self, description, product, vendor, version, businfo, config, capability):
        Computer.__init__(self, product)

	self.title_box(_(description) + _("Info"))
        self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("Name"), product))
	bodys.append((_("Vendor"), vendor))
        bodys.append((_("Bus addr"), businfo))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Driver"), config.get("driver")))
	bodys.append((_("Max power"), config.get("maxpower")))
	bodys.append((_("Speed"), config.get("speed")))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)


class Power(Computer):

    category = "battery"

    def __init__(self, description, product, vendor, version, slot, capacity, config):
        Computer.__init__(self, product)

	self.title_box(_(self.category) + _("Info"))
	self.tag_box(_("Basic Info"))

        bodys = []
	bodys.append((_("Name"), product))
        bodys.append((_("Vendor"), vendor))

        if capacity:
	    text = str(float(capacity) / 1000) + "Wh"
	    bodys.append((_("Bcapacity"), text))

	bodys.append((_("voltage"), config.get("voltage")))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)

class Generic(Computer):

    category = "generic"

    def __init__(self, description, product, vendor, version, businfo, serial, config, capability):
        Computer.__init__(self, product)

        if description:
            self.title_box(_(description))
        else:
            self.title_box(_(self.category))
        self.tag_box(_("Basic Info"))

        bodys = []
        if product:
            bodys.append((_("Name"), product))
        else:
            bodys.append((_("Name"), description))

	bodys.append((_("Vendor"), vendor))
	bodys.append((_("Bus addr"), businfo))
        self.body_box(bodys)

	self.tag_box(_("Expand Info"))

        del bodys[:]
	bodys.append((_("Firmware"), version))
        bodys.append((_("Driver"), config.get("driver")))
	bodys.append((_("Serial"), serial))
	bodys.append((_("Max power"), config.get("maxpower")))
	bodys.append((_("Speed"), config.get("speed")))
        self.body_box(bodys)

	self.logo = self.dev_logo(vendor)
