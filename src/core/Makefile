PACKAGENAME = lshw

CXX = c++
STRIP = strip
CXXFLAGS ?= -O3 -Wall

INCLUDES = `pkg-config --cflags python dbus-1`
LIBS = -lboost_python -llshw -lsensors -ldbus-1

SITE = $(shell python -c 'from distutils.sysconfig import get_python_lib;print get_python_lib()')

OBJS = main.o hw.o mem.o dmi.o cpuinfo.o osutils.o pci.o cpuid.o cdrom.o pcmcia-legacy.o scsi.o disk.o network.o fb.o options.o usb.o sysfs.o display.o heuristics.o cpufreq.o pcmcia.o smp.o abi.o jedec.o
SRCS = $(OBJS:.o=.cc)

all: lib$(PACKAGENAME).a $(PACKAGENAME).so

.cc.o:
	$(CXX) $(CXXFLAGS) -fPIC -c $< -o $@

lib$(PACKAGENAME).a: $(OBJS)
	$(AR) rs $@ $^

$(PACKAGENAME).so: lshw.cc lib$(PACKAGENAME).a 
	$(CXX) -L. -shared -fPIC $< -o $@ $(INCLUDES) $(LIBS) 
	$(STRIP) $@

install: $(PACKAGENAME).so
	mkdir -p $(DESTDIR)$(SITE)
	install -m 755 $(PACKAGENAME).so $(DESTDIR)$(SITE)
	
unstall:
	rm -f $(SITE)/$(PACKAGENAME).so
	
clean:
	rm -f $(OBJS) lib$(PACKAGENAME).a $(PACKAGENAME).so


