#(c) StartOS 2011/6 <hechao@ivali.com>

PREFIX = /usr
LIBDIR = $(PREFIX)/lib

.PHONY : install
.PHONY : uninstall

all:
	@echo "Makefile: Available actions: install, uninstall,"
	@echo "Makefile: Available variables: PREFIX, DESTDIR"
	
# install
install:
	python -u local.py
	-install -d $(DESTDIR)$(PREFIX)/bin/ $(DESTDIR)$(LIBDIR) $(DESTDIR)$(PREFIX)/share \
	$(DESTDIR)$(PREFIX)/share/dbus-1/system-services $(DESTDIR)/etc/dbus-1/system.d \
	$(DESTDIR)$(PREFIX)/share/polkit-1/actions  $(DESTDIR)$(PREFIX)/share/pixmaps/ \
	$(DESTDIR)$(PREFIX)/share/applications/
	-cp -r src/dbus/com.startos.ydm.service $(DESTDIR)$(PREFIX)/share/dbus-1/system-services
	-cp -r src/dbus/com.startos.ydm.conf $(DESTDIR)/etc/dbus-1/system.d
	-cp -r src/dbus/com.startos.ydm.policy $(DESTDIR)$(PREFIX)/share/polkit-1/actions
	-cp -r src/lib/ydevicemanager $(DESTDIR)$(LIBDIR)
	-cp -r src/share/locale $(DESTDIR)$(PREFIX)/share
	-cp -r src/share/ydevicemanager $(DESTDIR)$(PREFIX)/share
	-cp -r src/share/pci.ids $(DESTDIR)$(PREFIX)/share
	-cp -r src/share/usb.ids $(DESTDIR)$(PREFIX)/share
	-install src/bin/ydm $(DESTDIR)$(PREFIX)/bin/
	-install src/bin/ydm-cmd $(DESTDIR)$(PREFIX)/bin/
	-cp -r src/bin/ydm.png $(DESTDIR)$(PREFIX)/share/pixmaps/
	-install src/bin/ydm.desktop $(DESTDIR)$(PREFIX)/share/applications/
	-install src/bin/ydms.desktop $(DESTDIR)$(PREFIX)/share/applications/
	+make -C src/core install
	@echo "Makefile: ydm installed."


# uninstall
uninstall:
	rm -vf $(DESTDIR)$(PREFIX)/share/dbus-1/system-services/com.startos.ydm.service
	rm -vf $(DESTDIR)/etc/dbus-1/system.d/com.startos.ydm.conf
	rm -vf $(DESTDIR)$(PREFIX)/share/polkit-1/actions/com.startos.ydm.policy
	rm -rf $(DESTDIR)$(LIBDIR)/ydevicemanager
	rm -rf $(DESTDIR)$(PREFIX)/share/ydevicemanager
	rm -rf $(DESTDIR)$(PREFIX)/share/applications/ydm.desktop
	rm -rf $(DESTDIR)$(PREFIX)/share/applications/ydms.desktop
	rm -rf $(DESTDIR)$(PREFIX)/bin/ydm
	rm -rf $(DESTDIR)$(PREFIX)/bin/ydm-cmd
	rm -rf $(DESTDIR)$(PREFIX)/share/pixmaps/ydm.png
	+make -C src/core unstall


# clean	
clean:
	find src/ -name "*.pyc" -exec rm {} \;
	+make -C src/core clean
	


