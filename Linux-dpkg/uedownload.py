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

from lxml import etree
from uecommunication import uecommunication
import os
import tempfile
import subprocess
from ueinventory import ueinventory
import hashlib
from time import sleep

class uedownload():
	
	def download_action(self,urlinv,xml, options = None):
		root = etree.fromstring(xml)
		# download_launch is used to know if a download action append
		download_launch = None
		break_download_action = None
		try:
			for pack in root.findall('Package'):
				
				print 'Package: '+pack.find('Name').text
				mid = pack.find('Id').text
				pid = pack.find('Pid').text
				command = pack.find('Command').text
				if command.find('download_no_restart') != -1:
       	        	                break_download_action = False
       		        	        command = command.replace('\n',' && ')
				command = command.replace('&& download_no_restart','')
				command = command.replace('&& section_end','')
				url = pack.find('Url').text
				packagesum = pack.find('Packagesum').text
				download_launch = True
				try:
					uecommunication.send_xml(urlinv,'<Packstatus><Mid>'+mid+'</Mid><Pid>'+pid+'</Pid><Status>Ready to download and execute</Status></Packstatus>','status', options)
				except:
					return "Erreur uecommunication.send_xml / status"
				
				if packagesum != 'nofile':
					file_name = tempfile.gettempdir()+'/'+url.split('/')[-1]
					if self.download_tmp(url,file_name,packagesum) == 1:
						print 'Install in progress'
						uecommunication.send_xml(urlinv,'<Packstatus><Mid>'+mid+'</Mid><Pid>'+pid+'</Pid><Status>Install in progress</Status></Packstatus>','status', options)
						try:
							os.chdir(tempfile.gettempdir())
							error = str(subprocess.call(command, shell = True))
						except Exception as e:
							error = str(e)
					else :
						print 'Error when downloading' + file_name
					os.remove(file_name)
				else:
						print 'Install in progress'
						uecommunication.send_xml(urlinv,'<Packstatus><Mid>'+mid+'</Mid><Pid>'+pid+'</Pid><Status>Install in progress</Status></Packstatus>','status', options)
						try:
							os.chdir(tempfile.gettempdir())
							error = str(subprocess.call(command, shell = True))
						except Exception as e:
							error = str(e)
				if error !='0':
					uecommunication.send_xml(urlinv,'<Packstatus><Mid>'+mid+'</Mid><Pid>'+pid+'</Pid><Status>Error when executing action. Error code: '+error+'</Status></Packstatus>','status', options)
					break_download_action = True
				else:
					uecommunication.send_xml(urlinv,'<Packstatus><Mid>'+mid+'</Mid><Pid>'+pid+'</Pid><Status>Operation completed</Status></Packstatus>','status',options)
				sleep(5)
		except:
			return "Error detected when launching download_action"
		if download_launch:
			inventory = ueinventory.build_inventory()
			response_inventory = uecommunication.send_inventory(urlinv, inventory, options)
			# Break download action if an error occured during a previous install
			if break_download_action == None:
				self.download_action(urlinv,str(response_inventory[1]),options)
	
	def download_tmp(self,url,file_name,packagesum):
		try:
			print url
			print file_name
			print packagesum
			import urllib2
			if packagesum == None:
				return 1
			u = urllib2.urlopen(url)
			f = open(file_name, 'wb')
			meta = u.info()
			file_size = int(meta.getheaders("Content-Length")[0])
			print "Downloading: %s Bytes: %s" % (file_name, file_size)
		
			file_size_dl = 0
			block_sz = 8192
			while True:
				buffer = u.read(block_sz)
				if not buffer:
					break
				file_size_dl += len(buffer)
				f.write(buffer)
				status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
				status = status + chr(8)*(len(status)+1)
				print status,
			f.close()
			if self.md5_for_file(file_name) == packagesum:
				print ''
				return 1
			else :
				print 'md5 don\'t match: ' + self.md5_for_file(file_name) +' --- '+ packagesum
				return 0
		except:
			return "Error download_tmp"


	def md5_for_file(self, file_name,block_size=2**20):
		f = open(file_name, 'rb')
		md5 = hashlib.md5()
		while True:
			data = str(f.read(block_size))
			if not data:
				break
			md5.update(data)
		f.close()
		return str(md5.hexdigest())
