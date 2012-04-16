# -*- coding:utf-8 -*-

# Ylmf Device Manager(ydm).
# Copyright (C) 2011 YLMF, Inc.
# hechao <hechao@115.com>, 2011.
import os

R = 4
D = 10
S = 6
DEV_ID = 0
DRI_ID = 1
TEST_ID = 2
ICON = "/usr/share/ydevicemanager/"
LOGO = "/usr/share/ydevicemanager/logo/"

DEFAULT_FONT = "WenQuanYi Micro Hei"
DEFAULT_FONT_SIZE = 13

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 570

CONFIG = "/etc/yget.conf"
DBUS_IFACE = 'com.ylmf.ydm'
DBUS_PATH = '/com/ylmf/ydm'

HOME = os.path.expanduser("~")
TARGET_DIR = HOME + "/.ydm"
if not os.path.isdir(TARGET_DIR):
    #os.system("mkdir -p %s" %TARGET_DIR)
    os.mkdir(TARGET_DIR)
HW_XML = TARGET_DIR + "/device.xml"
TAR_XML = TARGET_DIR + "/device.tar"
RUN_DIR = os.path.abspath(os.path.dirname(__file__))

C_Errno = 1
P_Errno = 2

VENDORS = {
    #CPU产商
    "INTEL":["INTEL.jpg", "www.intel.com", "Intel"],
    "AMD":["AMD.jpg", "www.amd.com", "AMD"],
    "VIMICRO":["VIMICRO.jpg", "www.vimicro.com", "Vimicro"],
    #显卡产商
    "ATI":["ATI.jpg", "www.ati.com", "ATI"],
    "1002":["ATI.jpg", "www.ati.com", "ATI"],
    "1039":["SIS.jpg", "www.sis.com", "SIS"],
    "NVIDIA":["NVIDIA.jpg", "www.nvidia.com", "Nvidia"],
    "VIA":["VIA.jpg", "www.via.com.tw", "VIA"],
    "XFX":["XFX.jpg", "www.xfx.com.cn", "XFX"],
    "SUPERGRAPHIC":["SUPERGRAPHIC.jpg", "www.supergraphic.com.cn", "Supergraphic"],
    #显示器产商
    "AUO":["AUO.jpg", "www.auo.com", "AUO"],
    "AOC":["AOC.jpg", "www.aoc.com", "AOC"],
    "PHILIPS":["PHILIPS.jpg", "www.philips.com", "Philips"],
    "PHL":["PHILIPS.jpg", "www.philips.com", "Philips"],
    "LEN":["LENOVO.jpg", "www.lenovo.com", "Lenovo"],
    "SEC":["SAMSUNG.jpg", "www.samsung.com", "SAMSUNG"],
    #电脑品牌
    "HASEE":["HASEE.jpg", "www.hasee.com", "Hasee"],
    "FOUNDER":["FOUNDER.jpg", "www.founderpc.com", "Founder"],
    "TONGFANG":["TONGFANG.jpg", "www.tongfangpc.com", "Tongfang"],
    "TSINGHUA":["TONGFANG.jpg", "www.tongfangpc.com", "Tongfang"],
    "ACER":["ACER.jpg", "www.acer.com", "Acer"],
    "LENOVO":["LENOVO.jpg", "www.lenovo.com", "Lenovo"],
    "ASUSTEK":["ASUS.jpg", "www.asus.com", "ASUS"],
    "NEC":["NEC.jpg", "www.nec.com", "NEC"],
    "HP":["HP.jpg", "www.hp.com", "HP"],
    "HEWLETT-PACKARD":["HP.jpg", "www.hp.com", "HP"],
    "SAMSUNG":["SAMSUNG.jpg", "www.samsung.com", "SAMSUNG"],
    "TOSHIBA":["TOSHIBA.jpg", "www.toshiba.com", "TOSHIBA"],
    "APPLE":["APPLE.jpg", "www.apple.com", "Apple"],
    "DELL":["DELL.jpg", "www.dell.com", "DELL"],
    "FUJITSU":["FUJITSU.jpg", "www.fujitsu.com", "FUJITSU"],
    "SONY":["SONY.jpg", "www.sony.com", "SONY"],
    "IBM":["IBM.jpg", "www.ibm.com", "IBM"],
    #虚拟机
    "INNOTEK":["VIRTUALBOX.jpg", "www.virtualbox.org", "VirtualBox"],
    "VBOX":["VIRTUALBOX.jpg", "www.virtualbox.org", "VirtualBox"],
    "VIRTUALBOX":["VIRTUALBOX.jpg", "www.virtualbox.org", "VirtualBox"],
    #网卡产商
    "3COM":["3COM.jpg", "www.3com.com", "3COM"],
    "D-LINK":["D-LINK.jpg", "www.dlink.com.tw", "D-LINK"],
    "RALINK":["RALINK.jpg", "www.ralinktech.com", "Ralink"],
    "ATHEROS":["ATHEROS.jpg", "www.atheros.com", "Atheros"],
    "MARVELL":["MARVELL.jpg", "www.marvell.com", "Marvell"],
    "BROADCOM":["BROADCOM.jpg", "www.broadcom.com", "Broadcom"],
    #硬盘产商
    "EXCELSTOR":["EXCELSTOR.jpg", "www.excelstor.com", "Excelstor"],
    "HITACHI":["HITACHI.jpg", "www.hitachi.com", "Hitachi"],
    "MAXTOR":["MAXTOR.jpg", "www.maxtor.com", "Maxtor"],
    "WESTERN":["WDC.jpg", "www.wdc.com", "Western Digital"],
    "LITEON":["LITEON.jpg", "www.liteonit.com", "Liteon"],
    "SEAGATE":["SEAGATE.jpg", "www.seagate.com", "Seagate"],
    "QUANTUM":["QUANTUM.jpg", "www.quantum.com", "Quantum"],
    #光驱产商
    "PLDS":["PLDS.jpg", "www.pldsnet.com", "PLDS"],
    "HL-DT-ST":["LG.jpg", "www.lge.com", "LG"],
    "OPTIARC":["SONY.jpg", "www.sony-optiarc.com", "SONY"],
    "TSSTCORP":["TSSTCORP.jpg", "www.tsstorage.com", "TSSTcorp"],
    "PIONEER":["PIONEER.jpg", "www.pioneerchina.com", "Pioneer"],
    "MATSHITA":["PANASONIC.jpg", "www.panasonic.cn", "Panasonic"],
    #声卡产商
    "REALTEK":["REALTEK.jpg", "www.realtek.com.tw", "Realtek"],
    "CREATIVE":["CREATIVE.jpg", "www.creative.com", "Creative"],
    #摄像头
    "SONIX":["SONIX.jpg", "www.sonix.com.tw", "Sonix"],
    "ETRON":["ETRON.jpg", "www.etron.com.tw", "Etron"],
    "AVEO":["AVEO.jpg", "www.aveotek.com", "Aveotek"],
    "SYNTEK":["SYNTEK.jpg", "www.stk.com.tw", "Syntek"],
    "EMPIA":["EMPIA.jpg", "www.empiatech.com.tw", "EETI"],
    "CHICONY":["CHICONY.jpg", "www.chicony.com.tw", "Chicony"],
    "OMNIVISION":["OMNIVISION.jpg", "www.ovt.com", "OmniVision"],
    #鼠标产商
    "LOGITECH":["LOGITECH.jpg", "www.logitech.com", "Logitech"],
    "SUNPLUS":["SUNPLUS.jpg", "www.sunplus.com", "Sunplus"],
    "PRIMAX":["PRIMAX.jpg", "www.primax.com.cn", "Primax"],
    "PIXART":["PIXART.jpg", "www.pixart.com.tw", "Pixart"],
    "TRUST":["TRUST.jpg", "www.trust.com", "Trust"],
    "AVAGO":["AVAGO.jpg", "www.avagotech.cn", "Avago"],
    "MICROSOFT":["MICROSOFT.jpg", "www.microsoft.com", "Microsoft"],
    #键盘产商
    "RAPOO":["RAPOO.jpg", "www.rapoo.com", "Rapoo"],
    #主板产商
    "GIGABYTE":["GIGABYTE.jpg", "www.gigabyte.com.tw", "Gigabyte"],
    "BIOSTAR":["BIOSTAR.jpg", "www.biostar.com.tw", "Biostar"],
    "COLORFUL":["COLORFUL.jpg", "www.colorful.cn", "Colorful"],
    "YESTON":["YESTON.jpg", "www.yeston.net", "Yeston"],
    #指纹识别
    "UPEK":["AUTHENTEC.jpg", "www.authentec.com", "Authentec"],
    #闪存产商
    "KINGSTON":["KINGSTON.jpg", "www.kingston.com", "Kingston"],
    "KINGMAX":["KINGMAX.jpg", "www.kingmax.com", "Kingmax"],
    "HYNIX":["HYNIX.jpg", "www.hynix.com", "Hynix"],
    "MICRON":["MICRON.jpg", "www.micron.com", "Micron"],
    "06C1":["ASINT.jpg", "www.asinttech.com", "Asint"],
    "ADATA":["ADATA.jpg", "www.adata.com.cn", "ADATA"],
    "ZTE":["ZTE.jpg", "www.zte.com.cn", "ZTE"],
    "TEXAS":["TEXAS.jpg", "www.ti.com", "Texas Instruments"],
    #电源产商
    "SMP":["SMP.jpg", "www.simplo.com.tw", "SMP"],
    #BIOS产商
    "AMERICAN":["AMI.jpg", "www.ami.com", "AMI"],
    "AWARD":["PHOENIX.jpg", "www.award-bios.com", "Phoenix"],
    "PHOENIX":["PHOENIX.jpg", "www.phoenix.com", "Phoenix"]
}
