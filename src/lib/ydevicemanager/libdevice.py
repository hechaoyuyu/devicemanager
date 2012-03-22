#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__="hechao"
__date__ ="$2012-3-8 10:12:56$"

import os
import gtk
import time
import gobject
from threading import Thread

from globals import *
from widgets import BaseFucn
from devices import Device
from dbuscall import init_dbus

import gettext
gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)


class DeviceThread(Thread, gobject.GObject, BaseFucn):
    __gsignals__ = {
        'load-wait': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self, ydmg, flag=None):
	Thread.__init__(self)
        gobject.GObject.__init__(self)

        self.setDaemon(True)
        self.flag = flag
	self.base = ydmg

    def run(self):

        '''Wait'''
        self.base.framebox.add(self.load_wait(self.base, "Loading, please wait ..."))

	if not os.path.isfile(HW_XML) or self.flag == "TEST":
            '''set timeout is 600s, the default is 25s'''
            iface = init_dbus()
            iface.scan_device(timeout=600)
            iface.quit_loop()
            '''
            def f():
                iface = init_dbus()
                #set timeout is 600s, the default is 25s
                iface.scan_device(timeout=600)
                iface.quit_loop()

            fn = Thread(None, f)
            fn.start()

            n = 0
            while True:
                fn.join(0.2)
                if not fn.isAlive():
                    break
                n += 1
                ydmg.progressbar.set_fraction(float(n)/100)
            '''
	device = Device(HW_XML)
	self.dev_dict = device.dev_type
        self.base.pcid = device.pcid
        
	self.base.device_page = DevicePage(self.dev_dict, self.base)
        self.emit('load-wait')
	self.base.select_page(DEV_ID)


class DevicePage(gtk.VBox):

    def __init__(self, dev_dict, base):
	gtk.VBox.__init__(self)

	contentbox = gtk.HBox()

        #Prompt box
	self.tipbar = DeviceBar(base)
	self.pack_start(self.tipbar, False)

        #category box --> content view --> logo view
	self.categorybox = DeviceCategory(dev_dict, self.select)
	contentbox.pack_start(self.categorybox, False)

	self.contentview = DeviceContent(dev_dict)
	contentbox.pack_start(self.contentview)

	self.logoview = DeviceLoge(dev_dict)
	contentbox.pack_start(self.logoview, False)

	self.pack_start(contentbox)
	self.show_all()

    def select(self, widget, key):

	self.categorybox.categoryid = key
        #Image change, queue_draw() trigger expose()
	self.categorybox.queue_draw()
	self.contentview.updates(key)
	self.logoview.updates(key)


class DeviceBar(gtk.EventBox, BaseFucn):

    def __init__(self, base):
	gtk.EventBox.__init__(self)
	self.connect("expose_event", self.expose_ebox, ICON + "tip.png")

        self.base = base

	bar_box = gtk.HBox()
        align = self.define_align(bar_box, 0.5, 0.5, 1, 1)
        align.set_padding(0, 0, 10, 10)
        self.add(align)

	tip_label = gtk.Label()
	t = time.localtime(os.stat("/var/ypkg/packages/device.xml").st_mtime)
	date = time.strftime("%Y-%m-%d %H:%M:%S", t)
	tip_label.set_markup("<span foreground='#000000' font_desc='10'>%s</span>" % _("Date of last detection: ") + \
			 "<span color='red' font_desc='10'>%s</span>" % date)
	bar_box.pack_start(tip_label, False, False)

        '''TEST'''
        retest = self.re_tested("TEST")
        bar_box.pack_start(retest, False, False, 20)

        '''Save report'''
        report = self.report_scrot(ICON + "report.png", _("Generate reports"), "REPORT")
        bar_box.pack_end(report, False, False)

        '''Save screenshot'''
        screenshot = self.report_scrot(ICON + "scrot.png", _("Save screenshot"), "SCROT")
        bar_box.pack_end(screenshot, False, False, 20)

    def re_tested(self, has_tap):

        button = self.ebox_button()
        button.connect('button-press-event', self.on_click, has_tap)

        label = gtk.Label()
        label.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" % _("Re-tested"))

        button.add(label)
        return button

    def report_scrot(self, iconpath, txt, has_tap):

        button = self.ebox_button()
        button.connect('button-press-event', self.on_click, has_tap)

	icon = gtk.image_new_from_file(iconpath)
	label = gtk.Label()
	label.set_markup("<span foreground='#000000' font_desc='10'>%s</span>" % txt)

        box = gtk.HBox()
        box.pack_start(icon, False, False)
	box.pack_start(label, False, False, 4)
        button.add(box)

        return button

    def on_click(self, widget, event, has_tap):
	if has_tap == "REPORT":
            self.save_file_as()
        elif has_tap == "SCROT":
            os.system("gnome-screenshot -w")
        elif has_tap == "TEST":
            self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
            device_thread = DeviceThread(self.base, has_tap)
            device_thread.start()

    def save_file(self, fname):

        if fname:
            with open(fname, 'w') as fp:
                txt = self.read_file(HW_XML)
                fp.write(txt)
        else:
            self.save_file_as()

    def read_file(self, name):

        try:
            with open(name, 'r') as fp:
                return fp.read()
        except:
            return 'N/A'

    def save_file_as(self):

        fname = "device.xml"
        chooser = gtk.FileChooserDialog(_('Save report'),
                                        None, gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK)
                                       )

        chooser.set_current_name(fname)
        folder = os.path.expanduser('~')
        chooser.set_current_folder(folder)  # set default dir

        chooser.set_local_only(True)
        chooser.set_default_response(gtk.RESPONSE_OK)

        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            fname = chooser.get_filename()
            self.save_file(fname)
        elif res == gtk.RESPONSE_CANCEL:
            chooser.destroy()
        chooser.destroy()


class DeviceCategory(gtk.ScrolledWindow, BaseFucn):

    def __init__(self, dev_dict, func):
	gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)
	tab = gtk.gdk.pixbuf_get_file_info(ICON + "tab_h.png")
	self.set_size_request(tab[1] + 12, -1)

	self.callback = func

	keys = dev_dict.keys()
	keys.sort()
	self.categoryid = (0, "system")

	vbox = gtk.VBox(False)
        align = self.define_align(vbox)
        align.set_padding(10, 0, 6, 0)

	for key in keys:
	    button = self.draw_button(_(key[1]), ICON + "%s.png" % key[1], key)
            vbox.pack_start(button, False, False, 2)

	self.add_with_viewport(align)

	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#F5F8FA"))

    def draw_button(self, txt, icon, key):

	button = gtk.Button()
        button.connect("pressed", self.callback, key)

	h_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "tab_h.png")
	p_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "tab_p.png")

	button.set_size_request(h_pixbuf.get_width(), h_pixbuf.get_height())
	button.connect("expose_event", self.expose_tab, txt, icon, h_pixbuf, p_pixbuf, key, self.get_id)

	return button

    def get_id(self):
        return self.categoryid


class DeviceContent(gtk.ScrolledWindow):

    def __init__(self, dev_dict):
	gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)

	self.vbox = gtk.VBox()
	self.dev_dict = dev_dict

	self.key = (0, "system")
	self.updates(self.key)

	self.add_with_viewport(self.vbox)
	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))

    def updates(self, key):

	self.remove_box(self.vbox)
	for box in self.dev_dict[key]:
	    self.vbox.pack_start(box, False)

	self.vbox.show_all()

    def remove_box(self, box):
	box.foreach(lambda widget: box.remove(widget))


class DeviceLoge(gtk.ScrolledWindow, BaseFucn):

    def __init__(self, dev_dict):
	gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)
	self.set_size_request(200, -1)

	self.vbox = gtk.VBox()
	label = gtk.Label()
	label.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" % _("Hardware Brand"))
	self.align = self.define_align(label)
        self.align.set_padding(5, 0, 5, 0)

	self.dev_dict = dev_dict

	self.key = (0, "system")
	self.updates(self.key)

	self.add_with_viewport(self.vbox)
	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#F5F8FA"))

    def updates(self, key):

	self.remove_box(self.vbox)
	self.vbox.pack_start(self.align, False)
	for box in self.dev_dict[key]:
	    try:
		self.vbox.pack_start(box.logo, False)
	    except:
		self.vbox.show_all()

	self.vbox.show_all()

    def remove_box(self, box):
	box.foreach(lambda widget: box.remove(widget))
