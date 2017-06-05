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

import platform, subprocess
import re
from _winreg import *
import hashlib
import sys

class ueinventory(object):

    @staticmethod
    def build_inventory():
        self = ueinventory()
        manufacturer = self.get_manufacturer().strip()
        product = self.get_product().strip()
        serial = self.get_serial().strip()
        uuid = self.get_uuid().strip()
        domain = self.get_domain().strip()
        language = self.get_language().strip()
        hostname = self.get_hostname().strip()
        chassistype = self.get_chassistype().strip()
        osdata = self.format_oslist(self.get_oslist())
        ossum =  str(hashlib.md5(osdata).hexdigest())
        softwaredata = self.format_softlist(self.get_softwarelist())
        softsum = str(hashlib.md5(softwaredata).hexdigest()) 
        netdata = self.format_netlist(self.get_netlist())
        netsum =  str(hashlib.md5(netdata).hexdigest())
        username = self.get_username().strip()
        
        # Abort build_inventory if inventory presents too many errors
        if serial == manufacturer == product == domain == uuid == username == 'Unknown':
            raise Exception('To many detection error: build_inventory aborted') 

        data = "<Inventory>\n\
            <Hostname>"+hostname+"</Hostname>\n\
            <SerialNumber>"+serial+"</SerialNumber>\n\
            <Manufacturer>"+manufacturer+"</Manufacturer>\n\
            <Uuid>"+uuid+"</Uuid>\n\
            <UserName>"+username+"</UserName>\n\
            <Domain>"+domain+"</Domain>\n\
            <Language>"+language+"</Language>\n\
            <Product>"+product+"</Product>\n\
            <Chassistype>"+chassistype+"</Chassistype>\n\
            <Ossum>"+ossum+"</Ossum>\n\
            <Softsum>"+softsum+"</Softsum>\n\
            <Netsum>"+netsum+"</Netsum>\n\
            "+osdata+"\n\
            "+softwaredata+"\n\
            "+netdata+"</Inventory>"
        return (data, softsum)    

    def get_serial(self):
        try:
            args = 'wmic bios get serialnumber'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'

    def get_hostname(self):
        try:
            args = 'wmic computersystem get name'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unkown'

    def get_manufacturer(self):
        try:
            args = 'wmic csproduct get vendor'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'

    def get_product(self):
        try:
            args = 'wmic csproduct get name'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'

    def get_uuid(self):
        try:
            args = 'wmic path win32_computersystemproduct get uuid'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'
        
    def get_username(self):
        try:
            args = 'wmic computersystem get username'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            dom_user = p.stdout.readlines()[1]
            return dom_user.split('\\')[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'

    def get_domain(self):
        try:
            args = 'wmic computersystem get domain'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Unknown'

    def get_language(self):
        import locale
        try:
            return locale.getdefaultlocale()[0]
        except:
            return 'Unknown'

    def get_chassistype(self):
        chassis = ("Other","Unknown","Desktop","Low Profile Desktop","Pizza Box","Mini Tower",\
            "Tower","Portable","Laptop","Notebook","Hand Held","Docking Station","All in One",\
            "Sub Notebook","Space-Saving","Lunch Box","Main System Chassis","Expansion Chassis",\
            "Sub Chassis"," Bus Expansion Chassis","Peripheral Chassis","Storage Chass",\
            "Rack Mount Chassis","Sealed-Case PC")
        try:
            args = 'wmic systemenclosure get chassistypes'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            typestring =  p.stdout.readlines()[1]
            chassisnumber = int(re.findall(r'\d+',typestring)[0])
            return chassis[chassisnumber].decode(sys.stdout.encoding).encode('utf8')
        except:
            return 'Detection error'

    def get_softwarelist(self):     
        l = list()
        # try to read in registry for 64 bits OS
        try:
            aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
            aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",0, KEY_READ | KEY_WOW64_64KEY)
        
            for i in range(1024):
                try:
                    asubkey_name=EnumKey(aKey,i)
                    asubkey=OpenKey(aKey,asubkey_name)
                    val=QueryValueEx(asubkey, "DisplayName")
                    try:
                        vers = QueryValueEx(asubkey, "DisplayVersion")
                    except:
                        vers = ('undefined',)
                    try:
                        uninst = QueryValueEx(asubkey, "UninstallString")
                    except:
                        uninst = ('undefined',)
                    l.append(val[0].encode('utf-8')+',;,'+vers[0].encode('utf-8')+',;,'+uninst[0].encode('utf-8'))
                except:
                    pass
        except:
            pass
    
        # Then read on 32 bits, because 32bits version of python is used
        try:
            aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
            aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        
            for i in range(1024):
                try:
                    asubkey_name=EnumKey(aKey,i)
                    asubkey=OpenKey(aKey,asubkey_name)
                    val=QueryValueEx(asubkey, "DisplayName")
                    try:
                        vers = QueryValueEx(asubkey, "DisplayVersion")
                    except:
                        vers = ('undefined',)
                    try:
                        uninst = QueryValueEx(asubkey, "UninstallString")
                    except:
                        uninst = ('undefined',)
                                        # Prevent double detection for 32 bits systels
                    if not val[0].encode('utf-8')+',;,'+vers[0].encode('utf-8')+',;,'+uninst[0].encode('utf-8') in l:
                           l.append(val[0].encode('utf-8')+',;,'+vers[0].encode('utf-8')+',;,'+uninst[0].encode('utf-8'))
                except:
                    pass
        except:
            pass
        return l

    def format_softlist(self, slist):
        sdata =""
        for s in slist:
            s = self.encodeXMLText(s)
            line = s.split(',;,')
            if len(line) == 3:
                sdata += "<Software>\n\
                <Name>"+line[0].strip()+"</Name>\n\
                <Version>"+line[1].strip()+"</Version>\n\
                <Uninstall>"+line[2].strip()+"</Uninstall>\n\
                </Software>\n"
        return sdata


    def encodeXMLText(self,text):
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def get_netlist(self):
        args = 'wmic nicconfig get ipaddress, macaddress, ipsubnet /format:list'
        p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        netlist = list()     
        try:
            while True:
                n=p.stdout.readline()
                line=n.rstrip()
                if not n: break
                line = line.split('=')
                if len(line) == 2:
                    if line[1] != '' :
                        if line[0] == 'IPAddress':
                            ip = re.sub('[{"}]','', line[1])
                            ipsplit = ip.split(',')
                            if len(ipsplit) == 2:
                                ip = ipsplit[0]
                            n=p.stdout.readline()
                            line=n.rstrip()
                            line = line.split('=')
                            mask = re.sub('[{"}]','',line[1])
                            masksplit = mask.split(',')
                            if len(masksplit) == 2:
                                mask = masksplit[0]
                            n=p.stdout.readline()
                            line = n.rstrip()
                            line = line.split('=')
                            mac = line[1]
                            netlist.append(ip+','+mask+','+mac)
        except:
            print "Error when building netlist"
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
        args = 'wmic os get caption'
        p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:        
            if 'Windows XP' in p.stdout.readlines()[1]:
                args = 'wmic os get caption, csdversion, systemdrive /format:csv'
                p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                raw = p.stdout.readlines()[2]
                line = raw.split(',')
                if len(line) == 4:
                    name = line[1].strip().decode(sys.stdout.encoding).encode('utf8')
                    version = line[2].strip().decode(sys.stdout.encoding).encode('utf8')
                    systemdrive = line[3].strip().decode(sys.stdout.encoding).encode('utf8')
                try:
                    args = 'wmic computersystem get systemtype /format:csv'
                    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    raw = p.stdout.readlines()[2]
                    line = raw.split(',')
                    if '86' in line[1].strip():
                        arch = "32 bits"
                    elif '64' in line[1].strip():
                        arch = "64 bits"
                except:
                    arch = 'undefined'
                oslist.append(name+','+version+','+arch+','+systemdrive)
            else:
                args = 'wmic os get caption, csdversion, osarchitecture, systemdrive /format:list'
                p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                raw = p.stdout.readlines()
                name = raw[2].split("=",1)[1].strip().decode(sys.stdout.encoding).encode('utf8')
                version = raw[3].split("=",1)[1].strip().decode(sys.stdout.encoding).encode('utf8')
                arch = raw[4].split("=",1)[1].strip().decode(sys.stdout.encoding).encode('utf8')
                systemdrive = raw[5].split("=",1)[1].strip().decode(sys.stdout.encoding).encode('utf8')
                oslist.append(name+','+version+','+arch+','+systemdrive)
        except:
               oslist = ('Unkown, Unknown, Unknown, Unknown')
       
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


