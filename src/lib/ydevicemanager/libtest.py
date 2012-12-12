#!/usr/bin/env python
# -*- coding:utf-8 -*-
#__author__="hechao"
#__date__ ="$2012-5-8 15:20:40$"

import gtk
import time
from threading import Thread
from globals import *
from syscall import *
from widgets import BaseFucn

import gettext
gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)



class TestThread(Thread, BaseFucn):

    def __init__(self, ydmg):
        Thread.__init__(self)

        self.setDaemon(True)
        ydmg.lock = True
        self.base = ydmg

    def run(self):
        if self.base.testing == True:
            self.base.framebox.add(self.load_wait(self.base, _("Testing, please wait ...")))
            time.sleep(1)
            self.run_test()

        self.base.test_page = TestPage(self.base)
        self.base.lock = False

        if self.base.testing == True:
            self.base.select_page(TEST_ID)

    def run_test(self):
        self.base.statelabel.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" \
        % _("CPU performance testing is in progress ..."))
        time.sleep(1)
        pi = super_pi()

        self.base.statelabel.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" \
        % _("Memory performance testing is in progress ..."))
        time.sleep(1)
        mem = stream_triad()

        self.base.statelabel.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" \
        % _("Disk performance testing is in progress ..."))
        time.sleep(1)
        rwio = sysbench()

        self.base.statelabel.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" \
        % _("Card performance testing is in progress ..."))
        time.sleep(1)
        fps = gear_fps()

        fp = open(TEST_Z, 'w')
        fp.write("cpu = %s\nmem = %s\nr-io = %s\nw-io = %s\ncard = %s" \
                 %(pi, mem, rwio.get('read'), rwio.get('write'), fps))
        fp.close()


class TestPage(gtk.VBox):

    def __init__(self, base):
        gtk.VBox.__init__(self)

        #Tip bar
        tipbar = TestBar(base)
        self.pack_start(tipbar, False)

        #content view
        contentview = TestContent(base)
        self.pack_start(contentview)

        self.show_all()


class TestBar(gtk.EventBox, BaseFucn):

    def __init__(self, base):
        gtk.EventBox.__init__(self)
        self.connect("expose_event", self.expose_ebox, ICON + "tip.png")
        self.base = base

        bar_box = gtk.HBox()
        align = self.define_align(bar_box, 0.5, 0.5, 1, 1)
        align.set_padding(0, 0, 10, 10)
        self.add(align)

        tip_label = gtk.Label()

        self.flag = True
        if not os.path.isfile(TEST_Z) or not os.path.getsize(TEST_Z):
            self.flag = False
            tip_label.set_markup("<span font_desc='10'>%s</span>" % _("You are not on this machine hardware performance test!"))
        else:
            t = time.localtime(os.stat(TEST_Z).st_mtime)
            date = time.strftime("%Y-%m-%d %H:%M:%S", t)
            tip_label.set_markup("<span font_desc='10'>%s</span>" % _("Date of last detection: ") + \
                                 "<span color='red' font_desc='10'>%s</span>" % date)
	bar_box.pack_start(tip_label, False, False)

        rescan = self.re_tested("TEST")
        bar_box.pack_start(rescan, False, False, 20)

        '''Save screenshot'''
        screenshot = self.save_scrot("SCROT")
        bar_box.pack_end(screenshot, False, False)

    def re_tested(self, has_tap):

        button = self.ebox_button()
        button.connect('button-release-event', self.on_click, has_tap)
        if self.flag:
            txt = "Re-tested"
        else:
            txt = "At-tested"
        label = gtk.Label()
        label.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" % _(txt))

        button.add(label)
        return button

    def save_scrot(self, has_tap):

        button = self.ebox_button()
        button.connect('button-release-event', self.on_click, has_tap)

	icon = gtk.image_new_from_file(ICON + "scrot.png")
	label = gtk.Label()
	label.set_markup("<span font_desc='10'>%s</span>" % _("Save screenshot"))

        box = gtk.HBox()
        box.pack_start(icon, False, False)
	box.pack_start(label, False, False, 4)
        button.add(box)

        return button

    def on_click(self, widget, event, has_tap):
        if not self.active_zone(widget):
            return True

        if has_tap == "SCROT":
            screenshot()
        elif has_tap == "TEST":
            self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
            driver_thread = TestThread(self.base)
            self.base.testing = True
            driver_thread.start()
            self.base.has_tap = "TEST"


class TestContent(gtk.ScrolledWindow, BaseFucn):

    def __init__(self, base):
        gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)

        test_list = ["cpu", "mem", "r_io", "w_io", "card"]

        vbox = gtk.VBox(False, 10)
        align = self.define_align(vbox, 0.0, 0.0, 1, 1)
        align.set_padding(10, 0, 0, 0)

        for id in test_list:
            test_item = TestItem(id)
            vbox.pack_start(test_item, False, False)
            separator = gtk.HSeparator()
            vbox.pack_start(separator, False, False)

        self.add_with_viewport(align)
	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        self.show_all()


class TestItem(gtk.HBox, BaseFucn):

    def __init__(self, id):
        gtk.HBox.__init__(self)

        '''icons'''
        if id == "cpu":
            icon, vbox, ebox = self.test_cpu()
        elif id == "mem":
            icon, vbox, ebox = self.test_mem()
        elif id == "r_io":
            icon, vbox, ebox = self.test_rio()
        elif id == "w_io":
            icon, vbox, ebox = self.test_wio()
        else:
            icon, vbox, ebox = self.test_card()
        
        align = self.define_align(icon)
        align.set_padding(5, 5, 0, 0)
        self.pack_start(align, False, False, 10)

        align = self.define_align(vbox, 0, 0.5, 1.0)
        self.pack_start(align)
        if ebox:
            align = self.define_align(ebox, 0.0, 0.5, 1.0)
            self.pack_start(align, False, False, 15)

    def test_cpu(self):

        icon = gtk.image_new_from_file(ICON + "CPU.png")
        vbox = gtk.VBox()
        
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" % _("CPU performance"))
        vbox.pack_start(label, False, False)

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span font_desc='10'>%s</span>" % _("Test CPU data operation ability, the smaller the data processing ability of CPU stronger."))
        vbox.pack_start(label, False, False)

        ebox = None
        if os.path.isfile(TEST_Z) and os.path.getsize(TEST_Z):
            data = open(TEST_Z).read()
            value = re.findall("cpu = (.*)", data)[0]

            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            ebox.connect("expose_event", self.expose_ebox, ICON + "val_bg.png")

            label = gtk.Label()
            label.set_markup("<span foreground='#FFFFFF' font_desc='10'>%s</span>" %value)
            ebox.add(label)

        return icon, vbox, ebox

    def test_mem(self):

        icon = gtk.image_new_from_file(ICON + "MEM.png")
        vbox = gtk.VBox()

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" % _("Memory performance"))
        vbox.pack_start(label, False, False)

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span font_desc='10'>%s</span>" % _("Test memory read and write performance, the results of the greater read and write the faster."))
        vbox.pack_start(label, False, False)

        ebox = None
        if os.path.isfile(TEST_Z) and os.path.getsize(TEST_Z):
            data = open(TEST_Z).read()
            value = re.findall("mem = (.*)", data)[0]

            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            ebox.connect("expose_event", self.expose_ebox, ICON + "val_bg.png")

            label = gtk.Label()
            label.set_markup("<span foreground='#FFFFFF' font_desc='10'>%s</span>" %value)
            ebox.add(label)

        return icon, vbox, ebox

    def test_rio(self):

        icon = gtk.image_new_from_file(ICON + "DISK.png")
        vbox = gtk.VBox()

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" % _("Disk read performance"))
        vbox.pack_start(label, False, False)

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span font_desc='10'>%s</span>" % _("Test hard disk read performance, the results of the greater of hard disk read the faster."))
        vbox.pack_start(label, False, False)

        ebox = None
        if os.path.isfile(TEST_Z) and os.path.getsize(TEST_Z):
            data = open(TEST_Z).read()
            value = re.findall("r-io = (.*)", data)[0]

            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            ebox.connect("expose_event", self.expose_ebox, ICON + "val_bg.png")

            label = gtk.Label()
            label.set_markup("<span foreground='#FFFFFF' font_desc='10'>%s/s</span>" %value)
            ebox.add(label)

        return icon, vbox, ebox

    def test_wio(self):

        icon = gtk.image_new_from_file(ICON + "DISK.png")
        vbox = gtk.VBox()

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" % _("Disk write performance"))
        vbox.pack_start(label, False, False)

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span font_desc='10'>%s</span>" % _("Test hard disk write performance, the results of the greater of hard disk write the faster."))
        vbox.pack_start(label, False, False)

        ebox = None
        if os.path.isfile(TEST_Z) and os.path.getsize(TEST_Z):
            data = open(TEST_Z).read()
            value = re.findall("w-io = (.*)", data)[0]

            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            ebox.connect("expose_event", self.expose_ebox, ICON + "val_bg.png")

            label = gtk.Label()
            label.set_markup("<span foreground='#FFFFFF' font_desc='10'>%s/s</span>" %value)
            ebox.add(label)

        return icon, vbox, ebox

    def test_card(self):

        icon = gtk.image_new_from_file(ICON + "CARD.png")
        vbox = gtk.VBox()

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span foreground='#1C242D' font_desc='10'><b>%s</b></span>" % _("Card performance"))
        vbox.pack_start(label, False, False)

        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<span font_desc='10'>%s</span>" % _("Test graphics screen refresh rate, the results of the larger the screen the more smooth the better game support."))
        vbox.pack_start(label, False, False)

        ebox = None
        if os.path.isfile(TEST_Z) and os.path.getsize(TEST_Z):
            data = open(TEST_Z).read()
            value = re.findall("card = (.*)", data)[0]

            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            ebox.connect("expose_event", self.expose_ebox, ICON + "val_bg.png")

            label = gtk.Label()
            label.set_markup("<span foreground='#FFFFFF' font_desc='10'>%s</span>" %value)
            ebox.add(label)

        return icon, vbox, ebox

    def expose_ebox(self, widget, event, iconpath):

        pixbuf = gtk.gdk.pixbuf_new_from_file(iconpath)
	widget.set_size_request(pixbuf.get_width(), pixbuf.get_height())

        w, h = widget.allocation.width, widget.allocation.height
	cr = widget.window.cairo_create()
	cr.set_source_pixbuf(pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR), 0, 0)
        cr.paint()

        if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True


        