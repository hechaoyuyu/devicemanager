#include <unistd.h>
#include <stdio.h>
#include "hw.h"
#include "options.h"
#include "mem.h"
#include "dmi.h"
#include "cpuinfo.h"
#include "cpuid.h"
#include "pci.h"
#include "pcmcia.h"
#include "pcmcia-legacy.h"
#include "scsi.h"
#include "network.h"
#include "usb.h"
#include "sysfs.h"
#include "cpufreq.h"
#include "smp.h"
#include "abi.h"
#include "status.h"

bool scan_system(hwNode & system)
{
    char hostname[80];

    if(gethostname(hostname, sizeof(hostname)) == 0)
    {
        hwNode computer(::enabled("output:sanitize") ? "computer" : hostname, hw::system);

        status("DMI");
        if(enabled("dmi"))
            scan_dmi(computer);
        status("SMP");
        if(enabled("smp"))
            scan_smp(computer);
        status("memory");
        if(enabled("memory"))
            scan_memory(computer);
        status("/proc/cpuinfo");
        if(enabled("cpuinfo"))
            scan_cpuinfo(computer);
        status("CPUID");
        if(enabled("cpuid"))
            scan_cpuid(computer);
        status("PCI (sysfs)");
        if(enabled("pci"))
        {
            if(!scan_pci(computer))
            {
                if(enabled("pcilegacy"))
                    scan_pci_legacy(computer);
            }
        }
        else
        {
            status("PCI (legacy)");
            if(enabled("pcilegacy"))
                scan_pci_legacy(computer);
        }
        status("PCMCIA");
        if(enabled("pcmcia"))
            scan_pcmcia(computer);
        status("PCMCIA (legacy)");
        if(enabled("pcmcia-legacy"))
            scan_pcmcialegacy(computer);
        status("kernel device tree (sysfs)");
        if(enabled("sysfs"))
            scan_sysfs(computer);
        status("USB");
        if(enabled("usb"))
            scan_usb(computer);
        status("SCSI");
        if(enabled("scsi"))
            scan_scsi(computer);
        status("Network interfaces");
        if(enabled("network"))
            scan_network(computer);
        status("CPUFreq");
        if(enabled("cpufreq"))
            scan_cpufreq(computer);
        status("ABI");
        if(enabled("abi"))
            scan_abi(computer);

        if(computer.getDescription() == "")
            computer.setDescription("Computer");
        computer.assignPhysIds();
        computer.fixInconsistencies();

        system = computer;
    }
    else
        return false;

    return true;
}
