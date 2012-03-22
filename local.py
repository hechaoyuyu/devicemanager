#!/usr/bin/python

import os

print 'Preparing to install translation'
podir = os.path.join (os.path.realpath ("."), "po")
print podir
if os.path.isdir (podir):
	print 'installing translations'
	buildcmd = "msgfmt -o src/share/locale/%s/LC_MESSAGES/%s.mo po/%s.po"
	
	for name in os.listdir (podir):		
		if name.endswith('.po'):
			dname = name.split('-')[1].split('.')[0]
			name = name[:-3]
			
			print 'Creating language Binary for : ' + name
			if not os.path.isdir ("src/share/locale/%s/LC_MESSAGES" % dname):
				os.makedirs ("src/share/locale/%s/LC_MESSAGES" % dname)
			os.system (buildcmd % (dname,name.replace('-'+dname,''), name))
			
				

