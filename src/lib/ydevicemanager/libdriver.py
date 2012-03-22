#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__="hechao"
__date__ ="$2012-3-8 21:20:40$"

import gtk
import pango
import gobject
from threading import Thread

from globals import *
from widgets import BaseFucn
from drivers import Driver
from dbuscall import init_dbus
from syscall import environ, get_status


import gettext
gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)


class DriverThread(Thread, gobject.GObject):
    __gsignals__ = {
        'load-wait': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self, ydmg):
        Thread.__init__(self)
        gobject.GObject.__init__(self)

        self.setDaemon(True)
        self.base = ydmg

    def run(self):

        self.base.driver_page = DriverPage(self.base)
        self.emit('load-wait')


class DriverPage(gtk.VBox):

    def __init__(self, base):
        gtk.VBox.__init__(self)
        base.device_thread.join()

        drivers = Driver()
        if drivers.status:
            #Error
            warnwiew = WarnPage(drivers.output, base)
            self.pack_start(warnwiew)
        else:
            drivers.get_drivers()
            dri_list = drivers.dri_list
            
            #Prompt box
            tipbar = DriverBar(dri_list)
            self.pack_start(tipbar, False)

            #content view
            contentview = DriverContent(dri_list, base)
            self.pack_start(contentview)

        self.show_all()
  

class WarnPage(gtk.EventBox, BaseFucn):

    def __init__(self, output, base):
        gtk.EventBox.__init__(self)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        self.base = base

        warn_box = gtk.VBox()
        align = self.define_align(warn_box, 0.5, 0.5)
        self.add(align)

        tip_box = gtk.HBox()
	icon = gtk.image_new_from_file(ICON + "warn.png")
        tip_box.pack_start(icon, False)

        label = gtk.Label()
        label.set_markup("<span foreground='#000000' font_desc='10'>%s</span>" % _(output))
        tip_box.pack_start(label, False, False, 6)
        warn_box.pack_start(tip_box, False, False, 10)

        button = self.draw_button()
        align = self.define_align(button, 0.5, 0.5)
        warn_box.pack_start(align, False, False)

    def align_box(self, widget):

        align = gtk.Alignment()
        align.set(0.5, 0.5, 0.0, 0.0)
        align.add(widget)

        return align

    def draw_button(self):

        button = gtk.Button()
        label = gtk.Label()
        label.set_markup("<span font_desc='10'>%s</span>" % _("Retry"))
        button.add(label)
        button.connect("clicked", self.on_click)

        n_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "retry_n.png")
        h_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "retry_h.png")
        p_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "retry_p.png")
        button.set_size_request(n_pixbuf.get_width(), n_pixbuf.get_height())

	button.connect("expose_event", self.expose_button, n_pixbuf, h_pixbuf, p_pixbuf)

        return button

    def on_click(self, widget):

        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        driver_thread = DriverThread(self.base)
        driver_thread.start()
        self.base.has_tap = "RETRY"
        self.base.select_page(DRI_ID)


class DriverBar(gtk.EventBox, BaseFucn):

    def __init__(self, dri_list):
	gtk.EventBox.__init__(self)
	self.connect("expose_event", self.expose_ebox, ICON + "tip.png")

	bar_box = gtk.HBox()
        align = self.define_align(bar_box, 0.5, 0.5, 1.0, 1.0)
        align.set_padding(0, 0, 10, 10)
        self.add(align)
	tip_label = gtk.Label()
        tip_label.set_markup(_("Has detected that you have <span color='red' font_desc='10'>%s</span> hardware can be upgraded or installed driver!") % len(dri_list))

	bar_box.pack_start(tip_label, False, False)


class DriverContent(gtk.ScrolledWindow):

    def __init__(self, dri_list, base):
        gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)

        vbox = gtk.VBox()
        for key in dri_list.keys():
            for dri_tuple in dri_list[key]:
                id = base.pcid.get(key)
                if id:
                    dri_item = DriverItem(id, dri_tuple).item
                    vbox.pack_start(dri_item, False, False)
                    separator = gtk.HSeparator()
                    vbox.pack_start(separator, False, False)

        self.add_with_viewport(vbox)
	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        self.show_all()


class DriverItem(BaseFucn):

    def __init__(self, icon_type, dri_tuple):

        if icon_type == "display":
            icon = gtk.image_new_from_file(ICON + "card.png")
        elif icon_type == "network":
            icon = gtk.image_new_from_file(ICON + "net.png")
        elif icon_type == "multimedia":
            icon = gtk.image_new_from_file(ICON + "sound.png")
        else:
            icon = gtk.image_new_from_file(ICON + "usb.png")

        item_box = gtk.HBox()
        item_box.pack_start(icon, False, False, 6)

        vbox = gtk.VBox()
        align = self.define_align(vbox, 0.0, 0.5, 1.0)
        item_box.pack_start(align)

        pkgname = dri_tuple[1][0]
        name_label = gtk.Label()
        name_label.set_markup("<span font_desc='10'><b>%s</b></span>" % pkgname)
        name_label.set_alignment(0, 0)
        vbox.pack_start(name_label, False, False, 2)

        pkgsum = dri_tuple[1][2]
        self.sum_label = gtk.Label()
        self.sum_label.set_markup("<span font_desc='10'>%s</span>" % pkgsum)
        self.sum_label.set_alignment(0, 0)
        self.sum_label.set_tooltip_text(pkgsum)
        vbox.pack_start(self.sum_label)

        button = ActionButton(pkgname).button
        align = self.define_align(button, 0.0, 0.5, 1.0)
        item_box.pack_end(align, False, False, 6)

        pkgver = dri_tuple[1][1]
        ver_label = gtk.Label()
        ver_label.set_markup("<span font_desc='10'>%s</span>" % pkgver)
        item_box.pack_end(ver_label, False, False, 20)

        self.item = self.default_ebox()
        self.item.connect("size-allocate", self.label_align)
        self.item.add(item_box)
        
    def label_align(self, widget, event):
	self.sum_label.set_ellipsize(pango.ELLIPSIZE_END)

class ActionButton(BaseFucn):

    def __init__(self, pkgname):

        self.button = self.default_button()

        self.has_state = True

        self.label = gtk.Label()
        self.button.add(self.label)

        '''judge the installation state'''
        self.judge_install(pkgname)

        self.button.connect("clicked", self.on_click, pkgname)
        self.button.connect("enter", self.enter_button)
        self.button.connect("leave", self.leave_button)

    def judge_install(self, pkgname):
        status = get_status(pkgname)
        if status == "*":
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("install"))
            self.has_state = True
        elif status == "U":
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("update"))
            self.has_state = True
        else:
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("ainstall"))
            #self.set_sensitive(False)
            self.has_state = False

    def enter_button(self, widget):
        if not self.has_state:
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("uninstall"))

    def leave_button(self, widget):
        if not self.has_state:
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("ainstall"))

    def on_click(self, widget, pkgname):
        iface = init_dbus()
        if self.has_state:
            iface.install(pkgname, environ(), timeout=600)
        else:
            iface.uninstall(pkgname, environ(), timeout=600)

        self.judge_install(pkgname)
        iface.quit_loop()
