#!/usr/bin/env python

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


import optparse
import time
from ueinventory import ueinventory
from uecommunication import uecommunication
from uedownload import uedownload

def main():
# Define options
    parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
    parser.add_option("-s", "--server", dest="server", \
                   type="string", help="Your UpdatEngine server IP or DNS name")
    parser.add_option("-i", "--inventory", dest="inventory", \
                   action="store_false", help="Port of your UpdatEngine server")
    parser.add_option("-v", "--verbose", dest="verbose", \
                   action="store_false", help="Verbose mode")
    parser.add_option("-m", "--minutes", dest="minute", \
                   type="int", help="Minute between each inventory")
    parser.add_option("-c", "--cert", dest="cert", \
                   type="string", help="Absolute path to cacert.pem file")
    (options, args) = parser.parse_args()

    last = False
    if options.inventory is None:
        print "Just to test, inventory will not be send"
        last = True
    
    if options.minute is None:
        last = True

    download = uedownload()

    while True:
        
        try:
            inventory = ueinventory.build_inventory()
        except Exception:
            print "Error when building inventory"
            raise
        else:
            if inventory is not None:
                localtime   = time.localtime()
                print time.strftime("%Y-%m-%d-%H:%M:%S", localtime)
                print "Inventory built"

            if options.verbose is not None:
                print inventory
        
            if options.inventory is not None and options.server is not None:
                url = options.server+'/post/'
        
                try:    
                    response_inventory = uecommunication.send_inventory(url, inventory, options)
                except Exception:
                    print "Error on send_inventory process"
                    raise
                else:
                    print "Inventory sent to "+url
                    if options.verbose is not None:
                        print response_inventory
                    try:
                        download.download_action(url, str(response_inventory), options)
                    except Exception:
                        print "Error on download_action function"
                        raise
        if last:
            break
        else:
            time.sleep(options.minute*60)

if __name__ == "__main__":
    main()
