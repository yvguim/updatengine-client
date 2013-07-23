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
class ueinventory(object):

    @staticmethod
    def build_inventory():
        self = ueinventory()
        manufacturer = self.get_manufacturer()
        product = self.get_product()
        serial = self.get_serial()
        uuid = self.get_uuid()
        domain = self.get_domain()
        language = self.get_language()
        hostname = self.get_hostname()
        chassistype = self.get_chassistype()
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
            <Uuid>"+uuid.strip()+"</Uuid>\n\
            <Domain>"+domain.strip()+"</Domain>\n\
            <Language>"+language.strip()+"</Language>\n\
            <Product>"+product.strip()+"</Product>\n\
            <Chassistype>"+chassistype.strip()+"</Chassistype>\n\
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
            return p.stdout.readlines()[1]
        except:
            return 'Unknown'

    def get_hostname(self):
        try:
            p = platform.node()
            return p
        except:
            return 'Unkown'

    def get_manufacturer(self):
        try:
            args = 'wmic csproduct get vendor'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1]
        except:
            return 'Unknown'

    def get_product(self):
        try:
            args = 'wmic csproduct get name'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1]
        except:
            return 'Unknown'

    def get_uuid(self):
        try:
            args = 'wmic path win32_computersystemproduct get uuid'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1]
        except:
            return 'Unknown'
        
    def get_domain(self):
        try:
            args = 'wmic computersystem get domain'
            p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout.readlines()[1]
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
            return chassis[chassisnumber]
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
                    l.append(val[0].encode('utf-8')+','+vers[0].encode('utf-8')+','+uninst[0].encode('utf-8'))
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
                    if not val[0].encode('utf-8')+','+vers[0].encode('utf-8')+','+uninst[0].encode('utf-8') in l:
                           l.append(val[0].encode('utf-8')+','+vers[0].encode('utf-8')+','+uninst[0].encode('utf-8'))
                except:
                    pass
        except:
            pass
        return l

    def format_softlist(self, slist):
        sdata =""
        for s in slist:
            line = s.split(',')
            if len(line) == 3:
                sdata += "<Software>\n\
                <Name>"+line[0].strip()+"</Name>\n\
                <Version>"+line[1].strip()+"</Version>\n\
                <Uninstall>"+line[2].strip()+"</Uninstall>\n\
                </Software>\n"
        return sdata

    def get_netlist(self):
        args = 'wmic nicconfig get ipaddress, macaddress, ipsubnet /format:csv'
        p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        netlist = list()
        for n in p.stdout.readlines():
            line = n.split(',')
            if len(line) == 4:
                if line[1] != '' and line[0] != 'Node':
                    ip = re.sub('[{}]','', line[1])
                    ipsplit = ip.split(';')
                    if len(ipsplit) == 2:
                        ip = ipsplit[0]
                    
                    mask = re.sub('[{}]','',line[2])
                    masksplit = mask.split(';')
                    if len(masksplit) == 2:
                        mask = masksplit[0]
                
                    mac = line[3]
                    netlist.append(ip+','+mask+','+mac)
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
                    name = line[1].strip()
                    version = line[2].strip()
                    systemdrive = line[3].strip()
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
                name = raw[2].split("=",1)[1].strip()
                version = raw[3].split("=",1)[1].strip()
                arch = raw[4].split("=",1)[1].strip()
                systemdrive = raw[5].split("=",1)[1].strip()
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


