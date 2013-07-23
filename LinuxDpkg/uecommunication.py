
###############################################################################
# UpdatEngine - Software Packages Deployment and Administration tool          #
#                                                                             #
# Copyright (C) Yves Guimard - yves.guimard@gmail.com                         #
#                                                                             #
# This program is free software; you can redistribute it and/or               #
# modify it under the terms of the GNU General Public License                 #
# as published by the Free Software Foundation; either version 2              #
# of the License, or (at your option) any later version.                      #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,                  #
# MA  02110-1301, USA.                                                        #
###############################################################################

import ssl
import urllib, urllib2
import urlparse
from lxml import etree
from ueerrors import *

class uecommunication(object):

    def check_ssl(self, hostname, port, cafile_local):
        try:
            open(cafile_local,'r')
        except :
            print "Error in check_ssl (open function)"
            raise

        try:
            ssl.get_server_certificate((hostname, port), ca_certs=cafile_local)
        except ssl.SSLError:
            print "Error in check_ssl (ssl.get_server_certificate function)"
            raise ssl.SSLError('SSL cert of Host:'+str(hostname)+' Port:'+str(port)+' is invalid')  

    def printable(self, s):
        import string
        s = s.replace('&','&amp;')
        return filter(lambda x: x in string.printable, s)

    @staticmethod
    def send_xml(url,xml,action,options = None):
        self = uecommunication()
        xml = self.printable(xml)
        cookieHandler = urllib2.HTTPCookieProcessor()
        try:
            urlbits = urlparse.urlparse(url)
        except Exception:
            print "Error in send_xml (urlparse.urlparse function)"
            raise
        if options.cert is not None:
            try:
                if urlbits.scheme == 'https':
                    if ':' in urlbits.netloc:
                        hostname, port = urlbits.netloc.split(':')
                    else:
                        hostname = urlbits.netloc
                    if urlbits.port is None:
                        port = 443
                    else:
                        port = urlbits.port
                    self.check_ssl(hostname, int(port), options.cert)
            except:
                raise
        
        opener = urllib2.build_opener( urllib2.HTTPSHandler(), cookieHandler )
        urllib2.install_opener( opener )
        
        try:
            opener.open(url)
        except Exception:
            raise
        
        cookie = None
        for cookie in cookieHandler.cookiejar:
            if cookie.name == 'csrftoken':
                csrf_cookie = cookie
                break
        if cookie is None:
            raise IOError( "No csrf cookie found" )
        try:
            parameter = urllib.urlencode(dict(action=action,xml=xml,csrfmiddlewaretoken=csrf_cookie.value))
            req = urllib2.Request(url, parameter)
            req.add_header('Referer', url)
            response = urllib2.urlopen(req).read()
        except Exception:
            raise
        return response

    @staticmethod
    def printable_public_software(xml):
        try:
            root = etree.fromstring(xml)
        except:
            print xml
            print "Error in printable_public_software, bad xml format"
            raise
        
        for pack in root.findall('Package'):
            try:
                command = pack.find('Command').text
                if command.find('download_no_restart') != -1:
                    command = command.replace('\n',' && ')
                    command = command.replace('&& download_no_restart','')
                    command = command.replace('&& section_end','')

                print '---- Package number: %s ----' % pack.find('Pid').text
                print 'Package: %s' % pack.find('Name').text
                print 'Command associated to package: %s' % command
                print 'Url used to download package files (if needed): %s' % pack.find('Url').text
                print '----------------------------\n' 
            except:
                pass               

    @staticmethod
    def get_public_software_list(url, options = None, pack = None):
        self = uecommunication()
        cookieHandler = urllib2.HTTPCookieProcessor()
        try:
            urlbits = urlparse.urlparse(url)
        except Exception:
            print "Error in get_softlist (urlparse.urlparse function)"
            raise
        if options.cert is not None:
            try:
                if urlbits.scheme == 'https':
                    if ':' in urlbits.netloc:
                        hostname, port = urlbits.netloc.split(':')
                    else:
                        hostname = urlbits.netloc
                    if urlbits.port is None:
                        port = 443
                    else:
                        port = urlbits.port
                    self.check_ssl(hostname, int(port), options.cert)
            except:
                raise
        opener = urllib2.build_opener( urllib2.HTTPSHandler(), cookieHandler )
        urllib2.install_opener( opener )
        
        try:
            opener.open(url)
        except Exception:
            raise
        
        cookie = None
        for cookie in cookieHandler.cookiejar:
            if cookie.name == 'csrftoken':
                csrf_cookie = cookie
                break
        if cookie is None:
            raise IOError( "No csrf cookie found" )
        try:
            if pack is not None:
                parameter = urllib.urlencode(dict(action='softlist',pack=pack, csrfmiddlewaretoken=csrf_cookie.value))
            else:
                parameter = urllib.urlencode(dict(action='softlist',csrfmiddlewaretoken=csrf_cookie.value))
            req = urllib2.Request(url, parameter)
            req.add_header('Referer', url)
            response = urllib2.urlopen(req).read()
        except Exception:
            raise
        return response


    def valid_response(self, response):
        """Valid xml response after an inventory"""
        try:
            root  = etree.fromstring(response)  
        except Exception:
            raise UeReadResponse(response)

        if root.find('Import') is not None:
            if root.find('Import').text == 'Import ok':
                return response 
            else:
                raise UeImportError(response)
        else:
            raise UeResponseError(response)

    @staticmethod
    def send_inventory(url, xml, options = None):
        """Send an inventory to an updatengine server"""
        self = uecommunication()
        try:
            response = self.send_xml(url,xml,'inventory', options)
        except Exception:
            raise
        else:
            return self.valid_response(response)

