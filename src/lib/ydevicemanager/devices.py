#!/usr/bin/env python
# -*- coding: utf-8 -*-

# StartOS Device Manager(ydm).
# Copyright (C) 2011 ivali, Inc.
# hechao <hechao@ivali.com>, 2011.

__author__="hechao"
__date__ ="$2011-12-20 16:36:20$"

import gc
from xml.parsers import expat
from hwclass import *

class Device:

    def __init__(self, dev_xml):

        self.description = ''
        self.product = ''
        self.vendor = ''
        self.version = ''
        self.businfo = ''
        self.logicalname = ''
        self.date = ''
        self.serial = ''
	self.capacity = ''
        self.width = ''
	self.clock = ''
        self.slot = ''
        self.size = ''

        self.config = {}
        self.capability = []
        self.attr = {}

        self.dev_type = {}
        self.pcid = {}

        self._parser = expat.ParserCreate()
        self._parser.buffer_size = 102400
        self._parser.StartElementHandler = self.start_handler
        self._parser.CharacterDataHandler = self.data_handler
        self._parser.EndElementHandler = self.end_handler
        self._parser.returns_unicode = False

        fd = file(dev_xml)
        self._parser.ParseFile(fd)
        fd.close()

    def start_handler(self, tag, attrs):

        self.flag = tag

        if tag == "node":
            self.attr = attrs

        elif tag == "setting":
            self.config.setdefault(attrs["id"], attrs["value"])

        elif tag == "capability":
            self.capability.append(attrs["id"])

    def data_handler(self, data):

        if(data == '\n'):
            return
        if(data.isspace()):
            return

        if self.flag == "description":
            self.description = data.strip()

        elif self.flag == "product":
            self.product = data.strip()

        elif self.flag == "vendor":
            self.vendor = data.strip()

        elif self.flag == "businfo":
            self.businfo = data.strip()

        elif self.flag == "logicalname":
            self.logicalname = data.strip()

        elif self.flag == "version":
            self.version = data.strip()

        elif self.flag == "date":
            self.date = data.strip()

        elif self.flag == "serial":
            self.serial = data.strip()

	elif self.flag == "capacity":
            self.capacity = data.strip()

        elif self.flag == "width":
            self.width = data.strip()

	elif self.flag == "clock":
            self.clock = data.strip()

        elif self.flag == "slot":
            self.slot = data.strip()

        elif self.flag == "size":
            self.size = data.strip()

    def end_handler(self, tag):

        if tag == "node":
            
            if self.attr["class"] == "system":
                system = System(self.description, self.product, self.vendor, self.version, \
                self.serial, self.width, self.config, self.capability)
                self.dev_type.setdefault((0, "system"), []).append(system)
            
            elif self.attr["id"].split(":")[0] == "cpu" and self.attr["class"] == "processor":
                cpu = Cpu(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.serial, self.slot, self.size, self.capacity, self.width, self.clock, self.config, self.capability)
                self.dev_type.setdefault((1, "cpu"), []).append(cpu)

            elif self.attr["id"].split(":")[0] == "cache" and self.attr["class"] == "memory":
                cache = Cache(self.description, self.product, self.vendor, self.version, self.slot, self.size)
		self.dev_type.setdefault((1, "cpu"), []).append(cache)

            elif (self.attr["id"] == "core" or self.attr["id"] == "board") and self.attr["class"] == "bus":
                motherboard = Motherboard(self.description, self.product, self.vendor, self.version, self.serial)
		self.dev_type.setdefault((2, "motherboard"), []).append(motherboard)
            
            elif self.attr["id"] == "firmware" and self.attr["class"] == "memory":
                bios = Bios(self.description, self.product, self.vendor, self.version, \
                self.date, self.size, self.capability)
		self.dev_type.setdefault((2, "motherboard"), []).append(bios)

            elif self.attr["id"].split(":")[0] == "memory" and self.attr["class"] == "memory":
                memory = Memory(self.description, self.product, self.vendor, self.version, \
                self.slot, self.size)
		self.dev_type.setdefault((3, "memory"), []).append(memory)

            elif self.attr["id"].split(":")[0] == "bank" and self.attr["class"] == "memory":
                bank = Bank(self.description, self.product, self.vendor, self.version, \
                self.serial, self.slot, self.size, self.width, self.clock)
		self.dev_type.setdefault((3, "memory"), []).append(bank)

            elif self.attr["id"].split(":")[0] == "display" and self.attr["class"] == "display":
                display = Display(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.config, self.capability)
		self.dev_type.setdefault((4, "display"), []).append(display)
                self.pcid[display.pcid] = "display"
		if get_monitor():
		    monitor = Monitor("", "", "", "")
		    self.dev_type.setdefault((5, "monitor"), [monitor])#.append(monitor)

            elif self.attr["id"].split(":")[0] == "disk" and self.attr["class"] == "disk":
                disk = Disk(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.logicalname, self.serial, self.size, self.config, self.capability)
		self.dev_type.setdefault((6, "disk"), []).append(disk)

            elif self.attr["id"].split(":")[0] == "cdrom" and self.attr["class"] == "disk":
                cdrom = Cdrom(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.logicalname, self.config, self.capability)
		self.dev_type.setdefault((7, "cdrom"), []).append(cdrom)

            elif self.attr["class"] == "storage" and self.attr["handle"]:
                storage = Storage(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.logicalname, self.serial, self.config, self.capability)
		self.dev_type.setdefault((8, "storage"), []).append(storage)
            
            elif (self.attr["class"] == "network") or (self.attr["id"].split(":")[0] == "bridge" \
                and self.attr["class"] == "bridge"):
                network = Network(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.logicalname, self.serial, self.capacity, self.config, self.capability)
		self.dev_type.setdefault((9, "network"), []).append(network)
                self.pcid[network.pcid] = "network"

            elif self.attr["class"] == "multimedia":
                media = Multimedia(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.config, self.capability)
		self.dev_type.setdefault((10, "multimedia"), []).append(media)
                self.pcid[media.pcid] = "multimedia"

            elif self.attr["class"] == "input":
                imput = Imput(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.config, self.capability)
		self.dev_type.setdefault((11, "input"), []).append(imput)
                self.pcid[imput.pcid] = "input"

            elif self.attr["id"].split(":")[0] != "generic" and self.attr["class"] == "generic":
                generic = Generic(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.serial, self.config, self.capability)
		self.dev_type.setdefault((12, "generic"), []).append(generic)
                self.pcid[generic.pcid] = "generic"

            elif self.attr["id"].split(":")[0] != "communication" and self.attr["class"] == "communication":
                modem = Modem(self.description, self.product, self.vendor, self.version, \
                self.businfo, self.serial, self.config, self.capability)
		self.dev_type.setdefault((12, "generic"), []).append(modem)

            elif self.attr["id"].split(":")[0] == "battery" and self.attr["class"] == "power":
                power = Power(self.description, self.product, self.vendor, self.version, \
                self.slot, self.capacity, self.config)
		self.dev_type.setdefault((12, "generic"), []).append(power)
            
            self.clear()

    def clear(self):

        self.description = ''
        self.product = ''
        self.vendor = ''
        self.version = ''
        self.businfo = ''
        self.logicalname = ''
        self.date = ''
        self.serial = ''
	self.capacity = ''
        self.width = ''
	self.clock = ''
        self.slot = ''
        self.size = ''

        self.config = {}
        self.capability = []
        self.attr = {}

    def close(self):

        del self._parser
        gc.collect()
