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
import time
import shutil
class uedownload():
	urlinv = None
	xml = None
	options = None
	mid = None
	pid = None
	
	def download_action(self,urlinv,xml, options = None):
		self.urlinv = urlinv
		self.xml = xml
		self.options = options
		try:
			root = etree.fromstring(self.xml)
		except:
			print self.xml
			print "Error reading xml response in download_action"
			raise
		# download_launch is used to know if a download action append
		download_launch = None
		break_download_action = None
		try:
			for pack in root.findall('Package'):
				
				try:
					self.download_print_time()
					print 'Package: '+pack.find('Name').text
					self.mid = pack.find('Id').text
					self.pid = pack.find('Pid').text
					command = pack.find('Command').text
					if command.find('download_no_restart') != -1:
						break_download_action = False
						command = command.replace('\n',' && ')
					command = command.replace('&& download_no_restart','')
					command = command.replace('&& section_end','')
					url = pack.find('Url').text
					packagesum = pack.find('Packagesum').text
					download_launch = True
				except:
					print "Error in package xml format"
					raise

				self.download_send_status('Ready to download and execute')
				
				if packagesum != 'nofile':
					try:
						tmpdir = tempfile.gettempdir()+'/updatengine/'
						if not os.path.exists(tmpdir):
							os.makedirs(tmpdir)
						file_name = tmpdir+url.split('/')[-1]
						self.download_tmp(url,file_name,packagesum)
					except:
						self.download_print_time()
						print 'Error when downloading' + file_name
						self.download_send_status('Error downloading file '+file_name)
						raise
					else:
						print 'Install in progress'
						self.download_send_status('Install in progress')

						try:
							os.chdir(tmpdir)
							subprocess.check_call(command, shell = True)
						except Exception as inst:
							print "Error launching action"+command
							print type(inst)
							print inst
							self.download_send_status('Error when executing: '+command+' | Error code: '+str(inst))
							raise
						finally:
							# come back to gettemdir to remove updatengine directory
							os.chdir(tempfile.gettempdir())
							shutil.rmtree(tmpdir)
				else:
					print 'Install in progress'
					self.download_send_status('Install in progress')

					try:
						subprocess.check_call(command, shell = True)
					except Exception as inst:
						print "Error launching action"+command
						print type(inst)
						print inst
						self.download_send_status('Error when executing: '+command+' | Error code: '+str(inst))
						raise

				self.download_print_time()
				self.download_send_status('Operation completed')
				time.sleep(5)
		except:
			print "Error detected when launching download_action"
			raise
		else:	
			# Loop download action
			if download_launch:
				try:
					inventory = ueinventory.build_inventory()
					response_inventory = uecommunication.send_inventory(urlinv, inventory, options)
					# Break download action if an error occured during a previous install
					if break_download_action == None:
						self.download_action(urlinv,str(response_inventory),options)
				except:
					print "Error in Loop download action"
					raise
				print "End of download and install "
				self.download_print_time()
	
	
	
	def download_send_status(self,message):
		try:
			header = '<Packstatus><Mid>'+self.mid+'</Mid><Pid>'+self.pid+'</Pid><Status>'
			tail = '</Status></Packstatus>'
			full_message = header + message + tail
			uecommunication.send_xml(self.urlinv,full_message,'status',self.options)
		except:
			print "Erreur uecommunication.send_xml / status"
			raise



	def download_print_time(self):
		localtime   = time.localtime()
		print time.strftime("%Y-%m-%d-%H:%M:%S", localtime)



	def download_tmp(self,url,file_name,packagesum):
		from zipfile import ZipFile
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
				if str(file_name).lower().endswith('.zip'):
					ZipFile(file_name).extractall(tempfile.gettempdir()+'/updatengine/')
				return 1
			else :
				print 'md5 don\'t match: ' + self.md5_for_file(file_name) +' --- '+ packagesum
				return 0
		except:
			return "Error download_tmp"



	def md5_for_file(self, file_name,block_size=2**20):
		try:
			f = open(file_name, 'rb')
			md5 = hashlib.md5()
			while True:
				data = str(f.read(block_size))
				if not data:
					break
				md5.update(data)
			f.close()
		except:
			raise
		return str(md5.hexdigest())
