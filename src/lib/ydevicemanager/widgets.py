#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gtk
import locale
import cairo
from math import pi
from globals import *
import gettext
gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)


class BaseFucn:

    has_cursor = None

    def initwindow(self):

        window = gtk.Window()
        window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        gtk.window_set_default_icon_from_file(ICON + "logo.png")
        window.set_title(_("Device Manager"))

        #window.set_resizable(False)
        window.set_decorated(False)
        window.set_size_request(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        window.set_app_paintable(True)

        # receive all event masks
        window.set_events(gtk.gdk.ALL_EVENTS_MASK)

        window.connect("destroy", self.destroy)
        window.connect("size-allocate", self.size_allocate_event)
        window.connect("motion-notify-event", self.motion_notify)
        window.connect('button-press-event', self.resize_window)

        # supports alpha channels
        screen = window.get_screen()
        colormap = screen.get_rgba_colormap()
        if colormap:
            gtk.widget_set_default_colormap(colormap)

        window.set_geometry_hints(None, 600, 400)

        return window

    def destroy(self, widget):
        gtk.widget_pop_colormap()
	gtk.main_quit()

    def motion_notify(self, widget, event):
        (x, y) = widget.get_pointer()
        w, h = widget.allocation.width, widget.allocation.height
        
        if (x < D) and (y < D):
            # top left
            self.has_cursor = gtk.gdk.WINDOW_EDGE_NORTH_WEST
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_CORNER))
        elif (D < x < w - D - 120) and (y < D):
            # top side
            self.has_cursor = gtk.gdk.WINDOW_EDGE_NORTH
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.TOP_SIDE))
        #elif (x > w - D) and (y < D):
        #    # top right
        #    self.has_cursor = gtk.gdk.WINDOW_EDGE_NORTH_EAST
        #    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.TOP_RIGHT_CORNER))
        elif (x > w - D) and (D + 40 < y < h - D):
            # right side
            self.has_cursor = gtk.gdk.WINDOW_EDGE_EAST
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE))
        elif (x > w - D) and (y > h - D):
            # bottom right
            self.has_cursor = gtk.gdk.WINDOW_EDGE_SOUTH_EAST
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER))
        elif (D < x < w - D) and (y > h - D):
            # bottom side
            self.has_cursor = gtk.gdk.WINDOW_EDGE_SOUTH
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.BOTTOM_SIDE))
        elif (x < D) and (h - D < y < h):
            # bottom left
            self.has_cursor = gtk.gdk.WINDOW_EDGE_SOUTH_WEST
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.BOTTOM_LEFT_CORNER))
        elif (x < D) and (D < y < h - D):
            # left side
            self.has_cursor = gtk.gdk.WINDOW_EDGE_WEST
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE))
        else:
            widget.window.set_cursor(None)
            self.has_cursor = None

    def resize_window(self, widget, event):
        if self.has_cursor:
            self.window.begin_resize_drag(self.has_cursor, event.button, \
            int(event.x_root), int(event.y_root), event.time)

    def size_allocate_event(self, widget, allocation):

        w, h = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()

        # Clear the bitmap
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()

        # Draw our shape into the bitmap using cairo
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        self.draw_border(cr, 0, 0, w, h, R)
        cr.fill()

        # Set the window shape
        widget.shape_combine_mask(bitmap, 0, 0)

    def draw_border(self, cr, x, y, width, height, r):

	cr.move_to(x + r, y)
	cr.line_to(x + width - r, y)

	cr.move_to(x + width, y + r)
	cr.line_to(x + width, y + height)

	cr.move_to(x + width, y + height)
	cr.line_to(x, y + height)

	cr.move_to(x, y + height)
	cr.line_to(x, y + r)

	cr.arc(x + r, y + r, r, pi, 3 * pi / 2)
	cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi)
	cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
	cr.arc(x + r, y + height - r, r, pi / 2, pi)

    def load_wait(self, base, txt):

        ebox = gtk.EventBox()
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))

        vbox = gtk.VBox()
        align = self.define_align(vbox, 0.5, 0.5)
        ebox.add(align)

        animation = gtk.gdk.PixbufAnimation(ICON + "wait.gif")
        image = gtk.image_new_from_animation(animation)
        vbox.pack_start(image)

        base.statelabel = label = gtk.Label()
        base.statelabel.set_markup("<span foreground='#0092CE' font_desc='10'>%s</span>" % _(txt))
        vbox.pack_start(label)

        ebox.show_all()
        return ebox

        '''
        self.progressbar = gtk.ProgressBar()
        self.n = 0
        self.progressbar.set_fraction(0)
        self.progressbar.set_size_request(400,-1)
        waitbox.pack_start(self.progressbar)
        '''

    def define_align(self, widget, xa=0.0, ya=0.0, xc=0.0, yc=0.0):

        # gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
        align = gtk.Alignment(xa, ya, xc, yc)
        align.add(widget)

        return align

    def expose_tool(self, widget, event, txt, iconpath, h_pixbuf, p_pixbuf, pageid, get_pageid):

	icon = gtk.gdk.pixbuf_new_from_file(iconpath)
        id = get_pageid()

	if widget.state == gtk.STATE_NORMAL:
	    if id == pageid:
		pixbuf = p_pixbuf
	    else:
		pixbuf = None
	elif widget.state == gtk.STATE_PRELIGHT:
	    if id == pageid:
		pixbuf = p_pixbuf
	    else:
		pixbuf = h_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
	    pixbuf = p_pixbuf

	cr = widget.window.cairo_create()

	w_bg, h_bg = widget.allocation.width, widget.allocation.height
	x, y = widget.allocation.x, widget.allocation.y
	if pixbuf != None:
	    cr.set_source_pixbuf(pixbuf, x, y)
	    cr.paint()

	w_icon, h_icon = icon.get_width(), icon.get_height()

	cr.set_source_pixbuf(icon, x + (w_bg - w_icon) / 2, y + (h_bg - h_icon) / 2 - 10)
	cr.paint()

	font_size = 14
	x_font = x + w_bg / 2 - font_size * 2
	y_font = y + (h_bg + h_icon) / 2 + 8
	self.draw_font(cr, txt, font_size, "#FFFFFF", x_font, y_font)

	if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True

    def expose_tab(self, widget, event, txt, iconpath, h_pixbuf, p_pixbuf, key, get_id):

	icon = gtk.gdk.pixbuf_new_from_file(iconpath)
	select_id = get_id()

	if widget.state == gtk.STATE_NORMAL:
	    if select_id == key:
		color = "#FFFFFF"
		pixbuf = p_pixbuf
	    else:
		color = "#000000"
		pixbuf = None
	elif widget.state == gtk.STATE_PRELIGHT:
	    if select_id == key:
		color = "#FFFFFF"
		pixbuf = p_pixbuf
	    else:
		color = "#000000"
		pixbuf = h_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
	    color = "#FFFFFF"
	    pixbuf = p_pixbuf

	cr = widget.window.cairo_create()

	w_bg, h_bg = widget.allocation.width, widget.allocation.height
	x, y = widget.allocation.x, widget.allocation.y
	if pixbuf != None:
	    cr.set_source_pixbuf(pixbuf.scale_simple(w_bg, h_bg, gtk.gdk.INTERP_BILINEAR), x, y)
	    cr.paint()

	w_icon, h_icon = icon.get_width(), icon.get_height()

	cr.set_source_pixbuf(icon, x + w_icon / 2, y + (h_bg - h_icon) / 2 + 1)
	cr.paint()

	font_size = 13
	x_font = x + w_bg / 2 - font_size * 2 - 2
	y_font = y + (h_bg + h_icon) / 2 - 7
	self.draw_font(cr, txt, font_size, color, x_font, y_font)

	if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True

    def draw_font(self, cr, txt, font_size, color, x, y):

	cr.set_source_rgb(*self.select_color(color))
	cr.select_font_face(DEFAULT_FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(font_size)
	cr.move_to(x, y)
	cr.show_text(txt)

    def select_color(self, color):

	if color[0] == '#':
	    color = color[1:]
	(r, g, b) = (int(color[:2], 16),
		     int(color[2:4], 16),
		     int(color[4:], 16))
	return (r / 255.0, g / 255.0, b / 255.0)

    def expose_button(self, widget, event, n_pixbuf, h_pixbuf, p_pixbuf):

        if widget.state == gtk.STATE_NORMAL:
            pixbuf = n_pixbuf
	elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = h_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
	    pixbuf = p_pixbuf
        #if widget.has_focus():
        #    pixbuf = h_pixbuf
        
	cr = widget.window.cairo_create()

	x, y = widget.allocation.x, widget.allocation.y
	if pixbuf != None:
	    cr.set_source_pixbuf(pixbuf, x, y)
	    cr.paint()

        if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True

    def ebox_button(self):

        button = gtk.EventBox()
        button.set_visible_window(False)

	button.connect("enter-notify-event", self.enter_notify)
	button.connect("leave-notify-event", self.leave_notify)

        return button

    def enter_notify(self, widget, event):
        cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
        widget.window.set_cursor(cursor)

    def leave_notify(self, widget, event):
	widget.window.set_cursor(None)

    def active_zone(self, widget):

	mouse = widget.get_pointer()
        x = 0
        y = 0
        w = x + widget.get_allocation().width
        h = y + widget.get_allocation().height

        if mouse[0] > x and mouse[0] < w and mouse[1] > y and mouse[1] < h:
	    return True
	else:
	    return False

    def default_button(self):

        button = gtk.Button()
        button.set_size_request(80, 30)
        button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E9F5DF"))
        button.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("#E5F3D6"))
        button.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#E7f4DB"))

        return button

    def expose_ebox(self, widget, event, iconpath):

        pixbuf = gtk.gdk.pixbuf_new_from_file(iconpath)
	widget.set_size_request(-1, pixbuf.get_height())

        w, h = widget.allocation.width, widget.allocation.height
	cr = widget.window.cairo_create()
	cr.set_source_pixbuf(pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR), 0, 0)

        # Draw the background
        cr.set_operator(cairo.OPERATOR_SOURCE)
        #cr.set_source_rgba(0.1, 0.1, 0.1, 0.8)
        cr.paint()

        if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True

    def default_ebox(self):

        ebox = gtk.EventBox()
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))

        ebox.connect("enter_notify_event", self.enter_ebox)
        ebox.connect("leave_notify_event", self.leave_ebox)
        return ebox

    def set_eventbox(self, ebox):

        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
        ebox.connect("enter_notify_event", self.enter_ebox)
        ebox.connect("leave_notify_event", self.leave_ebox)

    def enter_ebox(self, widget, event):
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#F5F8FA"))

    def leave_ebox(self, widget, event):
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))

    def set_pixbuf(self, n, h, p):

        n_pixbuf = gtk.gdk.pixbuf_new_from_file(n)
        h_pixbuf = gtk.gdk.pixbuf_new_from_file(h)
        p_pixbuf = gtk.gdk.pixbuf_new_from_file(p)

        return n_pixbuf, h_pixbuf, p_pixbuf


class ToolBar(gtk.EventBox, BaseFucn):
    
    def __init__(self, ydmg):
        gtk.EventBox.__init__(self)
        self.connect("expose_event", self.expose_ebox, ICON + "top.png")
        self.connect('button-press-event', self.move_window)
        self.connect("button-press-event", self.double_click)

        self.base = ydmg
        self.has_max = True

        bar_box = gtk.VBox()
        # toprightbutton
        toggle_button = ToggleButton(self.min_window, self.max_window, self.close_window, self.get_hasmax)
        bar_box.pack_start(toggle_button, False)

        # toolbutton
        self.tool_button = ToolButton(ydmg)
        bar_box.pack_start(self.tool_button, False)

        self.add(bar_box)

    def get_hasmax(self):
	return self.has_max

    def move_window(self, widget, event):
        (x, y) = widget.get_pointer()
        w, h = widget.allocation.width, widget.allocation.height
        if D < x < w - D and y > D:
            self.base.window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def double_click(self, widget, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.max_window(widget)

    def max_window(self, widget):
	if self.has_max:
            self.base.window.maximize()
	else:
            self.base.window.unmaximize()

	self.has_max = not self.has_max

    def min_window(self, widget):
	self.base.window.iconify()

    def close_window(self, widget):
	self.base.window.hide_all()
	gtk.main_quit()


class ToolButton(gtk.HBox, BaseFucn):

    def __init__(self, ydmg):
	gtk.HBox.__init__(self)

        self.base = ydmg
	self.pageid = DEV_ID
        self.callback = ydmg.select_page

	'''symbol'''
        try:
            logo = gtk.image_new_from_file(ICON + "logo_%s.png" % locale.getlocale()[0])
        except:
            logo = gtk.image_new_from_file(ICON + "logo_en_US.png")
        align = self.define_align(logo, 0.0, 0.5)
        #set_padding(padding_top, padding_bottom, padding_left, padding_right)
        align.set_padding(0, 0, 20, 0)
        self.pack_start(align, False, False)

	button_box = gtk.HBox()
        align = self.define_align(button_box, 0.0, 0.5)
	self.pack_start(align)

	device_button = self.draw_button(_("DetectOn"), ICON + "device.png", DEV_ID)
	button_box.pack_start(device_button, False, False, 8)

	driver_button = self.draw_button(_("DriveOn"), ICON + "driver.png", DRI_ID)
	button_box.pack_start(driver_button, False, False, 8)

	test_button = self.draw_button(_("Reviews"), ICON + "test.png", TEST_ID)
	button_box.pack_start(test_button, False, False, 8)

    def draw_button(self, txt, iconpath, pageid):

	h_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "main_h.png")
	p_pixbuf = gtk.gdk.pixbuf_new_from_file(ICON + "main_p.png")

        button = gtk.Button()
	button.set_size_request(h_pixbuf.get_width(), h_pixbuf.get_height())

        button.connect("pressed", self.select_page, pageid)
	button.connect("expose_event", self.expose_tool, txt, iconpath, h_pixbuf, p_pixbuf, pageid, self.get_pageid)

	return button

    def select_page(self, widget, pageid):
        if self.base.lock:
            return True
    	self.callback(pageid)

    def get_pageid(self):
	return self.pageid


class ToggleButton(gtk.VBox, BaseFucn):

    def __init__(self, mincallback, maxcallback, closecallback, get_hasmax):
	gtk.VBox.__init__(self)

	self.get_hasmax = get_hasmax

        button_box = gtk.HBox()
        align = self.define_align(button_box, 1.0)
        self.add(align)

        min_button = self.draw_button(ICON + "min_n.png", ICON + "min_h.png", ICON + "min_p.png", mincallback)
        button_box.pack_start(min_button, False, False)

        max_button = self.draw_button(ICON + "max_n.png", ICON + "max_h.png", ICON + "max_p.png", maxcallback, flag=True)
        button_box.pack_start(max_button, False, False)

        close_button = self.draw_button(ICON + "close_n.png", ICON + "close_h.png", ICON + "close_p.png", closecallback)
        button_box.pack_start(close_button, False, False)

    def draw_button(self, n_bg, h_bg, p_bg, callback, flag=None):

        has_max = self.get_hasmax()
        if not has_max and flag:
            n_pixbuf, h_pixbuf, p_pixbuf = self.set_pixbuf(ICON + "max_nn.png", ICON + "max_hh.png", ICON + "max_pp.png")
        else:
            n_pixbuf, h_pixbuf, p_pixbuf = self.set_pixbuf(n_bg, h_bg, p_bg)

        button = gtk.Button()
        button.set_size_request(n_pixbuf.get_width(), n_pixbuf.get_height())

        button.connect("clicked", callback)
	button.connect("expose_event", self.expose_button, n_pixbuf, h_pixbuf, p_pixbuf)
        return button

class StatusBar(gtk.EventBox, BaseFucn):

    def __init__(self):
	gtk.EventBox.__init__(self)
        self.connect("expose_event", self.expose_ebox, ICON + "down.png")

	state_box = gtk.HBox()

        self.label = gtk.Label()
        align = self.define_align(self.label, 0.0, 0.5)
        align.set_padding(0, 0, 10, 0)

	if os.path.isfile(HW_XML):
	    self.label.set_markup("<span foreground='#A2A4A8' font_desc='10'>%s</span>" % _("Loading Finished"))
	else:
	    self.label.set_markup("<span foreground='#A2A4A8' font_desc='10'>%s</span>" % _("Initialization ..."))
        state_box.pack_start(align, False)

	osname = gtk.Label()
        align = self.define_align(osname, 0.0, 0.5)
        align.set_padding(0, 0, 0, 10)

        osname.set_markup("<span foreground='#A2A4A8' font_desc='10'>Ylmf OS 5.0</span>")
        state_box.pack_end(align, False)

	self.add(state_box)

    def set_status(self, status):
        self.label.set_markup("<span foreground='#A2A4A8' font_desc='10'>%s</span>" % status)
