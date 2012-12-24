PACKAGENAME = lshw

CXX = c++
STRIP = strip
CXXFLAGS ?= -O3 -Wall

##python2.6 or lower version##
#PYTHON_INC = $(shell python -c 'from distutils.sysconfig import get_python_inc;print get_python_inc()')
#INCLUDES=-I$(PYTHON_INC) `pkg-config --cflags dbus-1 cairo`
INCLUDES = `pkg-config --cflags python dbus-1 cairo`
LIBS = -lboost_python -lsensors -ldbus-1 -lcairo -fopenmp

SITE = $(shell python -c 'from distutils.sysconfig import get_python_lib;print get_python_lib()')

OBJS = main.o hw.o mem.o dmi.o cpuinfo.o osutils.o pci.o cpuid.o cdrom.o pcmcia-legacy.o \
scsi.o disk.o network.o options.o usb.o sysfs.o heuristics.o cpufreq.o pcmcia.o smp.o abi.o jedec.o
SRCS = $(OBJS:.o=.cc)

all: $(PACKAGENAME).so

.cc.o:
	$(CXX) $(CXXFLAGS) -fPIC -c $< -o $@

$(PACKAGENAME).so: lshw.cc stream.cc status.cc sensors.cc super.cc gears.cc $(OBJS)
	$(CXX) -L. -shared -fPIC $^ -o $@ $(INCLUDES) $(LIBS)
	$(STRIP) $@

install: $(PACKAGENAME).so
	mkdir -p $(DESTDIR)$(SITE)
	install -m 755 $(PACKAGENAME).so $(DESTDIR)$(SITE)
	
unstall:
	rm -f $(SITE)/$(PACKAGENAME).so
	
clean:
	rm -f $(OBJS) lib$(PACKAGENAME).a $(PACKAGENAME).so


