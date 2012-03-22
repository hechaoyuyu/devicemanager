#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import vte
import gtk
import gettext
import StringIO
__author__="hechao"
__date__ ="$2011-9-20 11:35:28$"

gettext.textdomain('ydm')
def _(s):
    return gettext.gettext(s)

class TWindow:
    def __init__(self):
        self.can_exit = self.flag = False
        self.terminal = vte.Terminal()
        self.terminal.connect('child-exited', lambda *w: self.child_exited())
        self.terminal.set_size_request(650, 420)
        self.window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_keep_above(True)
        window.add(self.terminal)
        window.connect('delete-event', self.delete_event)
        window.show_all()

    def delete_event(self, *w):
        if self.can_exit:
            os._exit(1)
        #elif self.flag:
        #    os._exit(0)
        else:
            return True

    def child_exited(self):

        exit_status = self.terminal.get_child_exit_status()
        if exit_status:
            self.can_exit = True
            self.terminal.feed('\n\r'
                               '\x1b[1;31m%s\x1b[m' % _('Command failed. Please close this window.'))
        else:
            os._exit(0)
            '''
            if self.flag:
                os._exit(0)
            else:
                self.flag = True
                self.terminal.feed('\n\r'
                                   '\x1b[1;31m%s\x1b[m' % _('Command succeed. Please close this window.'))

           '''

    def run(self, argv):
        self.window.set_title(_('ydm terminal') + ': ' + ' '.join(argv))
        assert isinstance(argv, list)

        msg = StringIO.StringIO()
        print >>msg, '\x1b[1;33m' + _('Run command:'), ' '.join(argv), '\x1b[m', '\r'
        self.terminal.feed(msg.getvalue())
        
        #if argv[0] == "curl" or argv[0] == "wget":
        #    self.flag = True

        pid = self.terminal.fork_command(command=argv[0], argv=argv)
        if pid == -1:
            self.terminal.feed('\n\r'
                               '\x1b[1;31m%s\x1b[m' % _('%s not find. Please close this window.') %argv[0])
            self.can_exit = True

if __name__ == "__main__":
    argv = sys.argv[1:]
    window = TWindow()
    window.run(argv)
    gtk.main()

