#!/usr/bin/env python
# -*- coding:utf-8 -*-
#__author__="hechao"
#__date__ ="$2012-3-8 21:20:40$"

import gtk
import pango
import gobject
from threading import Thread
from globals import *
from widgets import BaseFucn
from drivers import Driver
from dbuscall import init_dbus
from syscall import *


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
        ydmg.lock = True
        self.base = ydmg

    def run(self):
        self.base.driver_page = DriverPage(self.base)
        self.emit('load-wait')
        self.base.lock = False


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

            #judgment ncard+icard (temporary)
            icard = ncard = False
            for key in base.pcid:
                if base.pcid[key] == "display":
                    id = key.split(":")[0]
                    if id == "8086":
                        icard = True
                    elif id == "10DE":
                        ncard = True

            #Tip bar
            tipbar = DriverBar(dri_list, base, icard, ncard)
            self.pack_start(tipbar, False)

            #content view
            contentview = DriverContent(dri_list, base, icard, ncard)
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
        label.set_markup("<span font_desc='10'>%s</span>" % _(output))
        tip_box.pack_start(label, False, False, 6)
        warn_box.pack_start(tip_box, False, False, 10)

        button = self.draw_button()
        align = self.define_align(button, 0.5, 0.5)
        warn_box.pack_start(align, False, False)

    def draw_button(self):
 
        label = gtk.Label()
        label.set_markup("<span font_desc='10'>%s</span>" % _("Retry"))

        button = gtk.Button()
        button.add(label)
        
        n_pixbuf, h_pixbuf, p_pixbuf = self.set_pixbuf(ICON + "retry_n.png", ICON + "retry_h.png", ICON + "retry_p.png")
        button.set_size_request(n_pixbuf.get_width(), n_pixbuf.get_height())

        button.connect("clicked", self.on_click)
	button.connect("expose_event", self.expose_button, n_pixbuf, h_pixbuf, p_pixbuf)

        return button

    def on_click(self, widget):

        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        driver_thread = DriverThread(self.base)
        driver_thread.start()
        self.base.has_tap = "RETRY"
        self.base.select_page(DRI_ID)


class DriverBar(gtk.EventBox, BaseFucn):

    def __init__(self, dri_list, base, icard, ncard):
	gtk.EventBox.__init__(self)
	self.connect("expose_event", self.expose_ebox, ICON + "tip.png")
        self.base = base

	bar_box = gtk.HBox()
        align = self.define_align(bar_box, 0.5, 0.5, 1.0, 1.0)
        align.set_padding(0, 0, 10, 10)
        self.add(align)
        
	tip_label = gtk.Label()
        if (len(dri_list) == 0) or (icard and ncard):
            tip_label.set_markup("<span font_desc='10'>%s</span>" % _("You have installed the hardware required for driver!"))
        else:
            tip_label.set_markup(_("Has detected that you have <span color='red' font_desc='10'>%s</span> hardware can be upgraded or installed driver!") % len(dri_list))
	bar_box.pack_start(tip_label, False, False)

        rescan = self.re_scanned("SCAN")
        bar_box.pack_start(rescan, False, False, 20)

        '''Save screenshot'''
        screenshot = self.save_scrot("SCROT")
        bar_box.pack_end(screenshot, False, False)

    def re_scanned(self, has_tap):

        button = self.ebox_button()
        button.connect('button-release-event', self.on_click, has_tap)

        label = gtk.Label()
        label.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" % _("Re-scanned"))

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
        elif has_tap == "SCAN":
            self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
            driver_thread = DriverThread(self.base)
            driver_thread.start()
            self.base.has_tap = "RETRY"
            self.base.select_page(DRI_ID)

class DriverContent(gtk.ScrolledWindow, BaseFucn):

    def __init__(self, dri_list, base, icard, ncard):
        gtk.ScrolledWindow.__init__(self)
	self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	self.set_shadow_type(gtk.SHADOW_NONE)

        vbox = gtk.VBox()
        if (len(dri_list) == 0) or (icard and ncard):
            overpage = self.over_page()
            vbox.pack_start(overpage)

        for key in dri_list:
            for dri_tuple in list(set(dri_list[key])):
                if icard and ncard:
                    continue
                id = base.pcid.get(key)
                if id:
                    dri_item = DriverItem(id, dri_tuple)
                    vbox.pack_start(dri_item, False, False)
                    separator = gtk.HSeparator()
                    vbox.pack_start(separator, False, False)

        self.add_with_viewport(vbox)
	self.get_children()[0].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        self.show_all()

    def over_page(self):

        tip_box = gtk.HBox()
        icon = gtk.image_new_from_file(ICON + "over.png")
        tip_box.pack_start(icon, False)

        vbox = gtk.VBox(False, 4)
        tip_box.pack_start(vbox, False, False, 6)

        top_label = gtk.Label()
        top_label.set_alignment(0, 0)
        top_label.set_markup("<span font_desc='11'><b>%s</b></span>" % _("No need to install hardware device drivers!"))
        vbox.pack_start(top_label, False)

        bot_label = gtk.Label()
        bot_label.set_alignment(0, 0)
        bot_label.set_markup("<span font_desc='10'>%s</span>" % _("If you recently added hardware, please click 'Rescan'!"))
        vbox.pack_start(bot_label, False)

        align = self.define_align(tip_box, 0.5, 0.5)
        return align

class DriverItem(gtk.EventBox, BaseFucn):

    def __init__(self, icon_type, dri_tuple):
        gtk.EventBox.__init__(self)
        self.set_eventbox(self)

        '''icons'''
        if icon_type == "display":
            icon = gtk.image_new_from_file(ICON + "card.png")
        elif icon_type == "network":
            icon = gtk.image_new_from_file(ICON + "net.png")
        elif icon_type == "multimedia":
            icon = gtk.image_new_from_file(ICON + "sound.png")
        else:
            icon = gtk.image_new_from_file(ICON + "usb.png")
        align = self.define_align(icon)
        align.set_padding(5, 5, 0, 0)

        item_box = gtk.HBox()
        item_box.pack_start(align, False, False, 10)

        '''vbox --> (name_label,sum_label)'''
        vbox = gtk.VBox(False, 4)
        align = self.define_align(vbox, 0, 0.5, 1.0)
        item_box.pack_start(align)

        '''pkg info'''
        pkgname = dri_tuple[1][0]
        name_label = gtk.Label()
        name_label.set_markup("<span font_desc='10'><b>%s</b></span>" % pkgname)
        name_label.set_alignment(0, 0)
        vbox.pack_start(name_label, False, False)
        
        pkgsum = dri_tuple[1][2]
        self.sum_label = gtk.Label()
        self.sum_label.set_markup("<span font_desc='10'>%s</span>" % pkgsum)
        self.sum_label.set_alignment(0, 0)
        self.sum_label.set_tooltip_text(pkgsum)
        vbox.pack_start(self.sum_label)

        '''action button'''
        pkgmod = dri_tuple[0]
        button = ActionButton(pkgname, pkgmod)
        button.connect("focus-in-event", self.get_focus)
        button.connect("focus-out-event", self.lose_focus)
        align = self.define_align(button, 0.0, 0.5, 1.0)
        item_box.pack_end(align, False, False, 15)

        '''pkg version'''
        pkgver = dri_tuple[1][1]
        ver_label = gtk.Label()
        ver_label.set_markup("<span font_desc='10'>%s</span>" % pkgver)
        item_box.pack_end(ver_label, False, False, 20)

        '''ebox --> item_box --> (vbox,button,ver_label)'''
        #self.item = self.default_ebox()
        self.connect("size-allocate", self.label_align)
        self.add(item_box)
        
    def label_align(self, widget, event):
        try:
            self.sum_label.set_ellipsize(pango.ELLIPSIZE_END)
        except:pass

    def get_focus(self, widget, event):
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#F5F8FA"))

    def lose_focus(self, widget, event):
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))


class ActionButton(gtk.Button, BaseFucn):

    def __init__(self, pkgname, pkgmod):
        gtk.Button.__init__(self)
        self.has_state = True

        self.label = gtk.Label()

        '''judge the installation state'''
        self.judge_install(pkgname)

        self.set_size_request(self.n_pixbuf.get_width(), self.n_pixbuf.get_height() + 2)
        self.add(self.label)
        self.set_alignment(0.5, 1)

        self.connect("expose_event", self.expose_button, self.n_pixbuf, self.h_pixbuf, self.p_pixbuf)
        self.connect("clicked", self.on_click, pkgname, pkgmod)
        self.connect("enter", self.enter_button)
        self.connect("leave", self.leave_button)

    def judge_install(self, pkgname):
        
        status = get_status(pkgname)
        if status == "*":
            self.n_pixbuf, self.h_pixbuf, self.p_pixbuf = self.set_pixbuf(ICON +\
            "install_n.png", ICON + "install_h.png", ICON + "install_p.png")
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("install"))
            self.has_state = True
        elif status == "U":
            self.n_pixbuf, self.h_pixbuf, self.p_pixbuf = self.set_pixbuf(ICON +\
            "update_n.png", ICON + "update_h.png", ICON + "update_p.png")
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("update"))
            self.has_state = True
        else:
            self.n_pixbuf, self.h_pixbuf, self.p_pixbuf = self.set_pixbuf(ICON +\
            "uninstall_n.png", ICON + "uninstall_h.png", ICON + "uninstall_p.png")
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("ainstall"))
            #self.set_sensitive(False)
            self.has_state = False

    def enter_button(self, widget):
        if not self.has_state:
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("uninstall"))

    def leave_button(self, widget):
        if not self.has_state:
            self.label.set_markup("<span font_desc='10'>%s</span>" % _("ainstall"))

    def on_click(self, widget, pkgname, pkgmod):
        
        iface = init_dbus()
        if self.has_state:
            if lsmod(pkgmod):
                if self.show_dialog():
                    '''set timeout is 600s, the default is 25s'''
                    iface.install(pkgname, environ(), timeout=600)
            else:
                 iface.install(pkgname, environ(), timeout=600)
        else:
            iface.uninstall(pkgname, environ(), timeout=600)

        self.judge_install(pkgname)
        iface.quit_loop()

    def show_dialog(self):

        dialog = gtk.Dialog(_('DriveOn'),
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))

        dialog.set_resizable(False)
        dialog.set_default_response(gtk.RESPONSE_REJECT)

        warn_box = gtk.VBox()
        warn_box.show()

        align = self.define_align(warn_box, 0.5, 0.5)
        align.show()
        dialog.vbox.pack_start(align)

        tip_box = gtk.HBox()
        tip_box.show()
        warn_box.pack_start(tip_box, False, False)

	icon = gtk.image_new_from_file(ICON + "test.png")
        icon.show()
        tip_box.pack_start(icon, False)

        label = gtk.Label()
        label.show()
        label.set_markup("<span font_desc='10'>%s</span>" % _("The system has the corresponding drive loading,continue?"))
        tip_box.pack_start(label, False, False, 6)
        
        res = dialog.run()
        dialog.destroy()
        
        if res == gtk.RESPONSE_OK:
            return True
        if res == gtk.RESPONSE_REJECT:
            return False
