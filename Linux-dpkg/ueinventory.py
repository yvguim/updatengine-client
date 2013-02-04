###################################################################################
# UpdatEngine - Software Packages Deployment and Administration tool              #  
#                                                                                 #
# Copyright (C) Yves Guimard - yves.guimard@gmail.com                             #
#                                                                                 #
# This program is free software; you can redistribute it and/or                   #
# modify it under the terms of the GNU General Public License                     #
# as published by the Free Software Foundation; either version 2                  #
# of the License, or (at your option) any later version.                          #
#                                                                                 #
# This program is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                  #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   #
# GNU General Public License for more details.                                    #
#                                                                                 #
# You should have received a copy of the GNU General Public License               #
# along with this program; if not, write to the Free Software                     #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA. #
###################################################################################

import platform
import subprocess
import os
import dmidecode
import hashlib
class ueinventory():

	@staticmethod
	def build_inventory():
	 # Check if root user
		root = (os.getuid() == 0)
		if not root:
			raise StandardError("#### Program stopped: You MUST use this program as root user ###")
		else:
			self = ueinventory()
			dmixml = dmidecode.dmidecodeXML()
			dmixml.SetResultType(dmidecode.DMIXML_DOC)
			xmldoc = dmixml.QuerySection('all')
			dmixp = xmldoc.xpathNewContext()
			
			manufacturer = self.get_manufacturer(dmixp)
			product = self.get_product(dmixp)
			serial = self.get_serial(dmixp)
			chassistype = self.get_chassistype(dmixp)
			hostname = self.get_hostname()
			osdata = self.format_oslist(self.get_oslist())
			ossum =  str(hashlib.md5(osdata).hexdigest())
			softwaredata = self.format_softlist(self.get_softwarelist())
			softsum = str(hashlib.md5(softwaredata).hexdigest()) 
			netdata = self.format_netlist(self.get_netlist())
			netsum =  str(hashlib.md5(netdata).hexdigest())
			data = "<Inventory>\n\
				<Hostname>"+hostname.strip()+"</Hostname>\n\
				<SerialNumber>"+serial.strip()+"</SerialNumber>\n\
				<Manufacturer>"+manufacturer.strip()+"</Manufacturer>\n\
				<Product>"+product.strip()+"</Product>\n\
				<Chassistype>"+chassistype.strip()+"</Chassistype>\n\
				<Ossum>"+ossum+"</Ossum>\n\
				<Softsum>"+softsum+"</Softsum>\n\
				<Netsum>"+netsum+"</Netsum>\n\
				"+osdata+"\n\
				"+softwaredata+"\n\
				"+netdata+"\n\
				</Inventory>"

			return data


	def checkdmi(self, dmixp,tag):
		try:
			return dmixp.xpathEval(tag)[0].get_content()
		except:
			return "Unknown"

	def get_manufacturer(self, dmixp):
		try:
			return self.checkdmi(dmixp,'/dmidecode/SystemInfo/Manufacturer')
		except:
			return'Unknown'
	def get_product(self, dmixp):
		try:
			return self.checkdmi(dmixp,'/dmidecode/SystemInfo/ProductName')
		except:
			return 'Unknown'
	def get_serial(self, dmixp):
		try:
			return self.checkdmi(dmixp,'/dmidecode/SystemInfo/SerialNumber')
		except:
			return 'Unknown'

	def get_chassistype(self, dmixp):
		try:
			return self.checkdmi(dmixp,'/dmidecode/ChassisInfo/ChassisType')
		except:
			return 'Unknown'

	def get_hostname(self):
		try:
			return platform.node()
		except:
			return 'Unknown'

	def get_softwarelist(self):
		try:
			cmd = 'dpkg -l |awk \'/^ii/ {print $2","$3}\''
			p = subprocess.Popen([cmd],stdout=subprocess.PIPE, shell=True)
			l = list()
			for s in p.stdout.readlines():
				l.append(s.encode('utf-8'))
			return l
		except:
			return []

	def format_softlist(self, slist):
		sdata =""
		for s in slist:
			line= s.split(',')
			if len(line) == 2:
				sdata += "<Software>\n\
				<Name>"+line[0].strip()+"</Name>\n\
				<Version>"+line[1].strip()+"</Version>\n\
				<Uninstall>Defined only for Windows hosts</Uninstall>\n\
				</Software>\n"
		return sdata

	def get_netlist(self):
		import netifaces
		netnamelist = netifaces.interfaces()
		netlist = list()
		for net in netnamelist:
			try:
				ip = netifaces.ifaddresses(net)[netifaces.AF_INET][0]['addr']
				mask = netifaces.ifaddresses(net)[netifaces.AF_INET][0]['netmask']
				mac = netifaces.ifaddresses(net)[netifaces.AF_LINK][0]['addr']
				netlist.append(ip+','+mask+','+mac)
			except :
				pass
		return netlist

	def format_netlist(self, netlist):
		ndata =""
		for n in netlist:
			line = n.split(',')
			if len(line) == 3:
				ndata += "<Network>\n\
				<Ip>"+line[0].strip()+"</Ip>\n\
				<Mask>"+line[1].strip()+"</Mask>\n\
				<Mac>"+line[2].strip()+"</Mac>\n\
				</Network>\n"
		return ndata

	def get_oslist(self):
		oslist = list()
		ostuple = platform.linux_distribution()
		name = ostuple[0]
		version = ostuple[1] +' - ' + ostuple[2]
		arch = os.uname()[4]
		systemdrive = '-'
		oslist.append(name+','+version+','+arch+','+systemdrive)
		return oslist

	def format_oslist(self, oslist):
		osdata =""
		for o in oslist:
			line = o.split(',')
			if len(line) == 4:
				osdata += "<Osdistribution>\n\
				<Name>"+line[0].strip()+"</Name>\n\
				<Version>"+line[1].strip()+"</Version>\n\
				<Arch>"+line[2].strip()+"</Arch>\n\
				<Systemdrive>"+line[3].strip()+"</Systemdrive>\n\
				</Osdistribution>\n"
		return osdata



