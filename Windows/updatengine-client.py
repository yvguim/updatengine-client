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
import logging
from ueinventory import ueinventory
from uecommunication import uecommunication
from uedownload import uedownload

def wait(minutes, passphrase):
    import socket
    from datetime import datetime, timedelta
    socket.setdefaulttimeout(minutes*60)
    Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    Host = ''
    Port = 2010
    Sock.bind((Host,Port))
    Sock.listen(1)
    limit = datetime.now()+timedelta(minutes=minutes)
    print "wait for connexion with passphrase %s or %s" % (passphrase, limit)
    try:
        client, adresse = Sock.accept()
        while datetime.now() < limit:
            RequeteDuClient = client.recv(255)
            print RequeteDuClient
            if RequeteDuClient == passphrase:
                Sock.close()
                return
    except socket.timeout:
        Sock.close()
    return

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
    parser.add_option("-l", "--list", dest="list", \
                   action="store_false", help="To get public soft list")
    parser.add_option("-g", "--get", type = "int", dest="get", \
                   help="Package number to install  manualy")
    parser.add_option("-o", "--out", type = "string", dest="out", \
                   help="Full path to logfile")
    (options, args) = parser.parse_args()

    if options.out is not None:
        try:
            logging.basicConfig(level=logging.DEBUG, filename=options.out)
        except:
            logging.basicConfig(level=logging.DEBUG, filename='updatengine-client.log')
            logging.exception("can't write on "+options.out+" file use default file instead")
    else:
        logging.basicConfig(level=logging.DEBUG, filename='updatengine-client.log')

    last = False

    if options.list is not None and options.server is not None:
        logging.info("*********************************\n")
        localtime   = time.localtime()
        logging.info("Start: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))
        
        print "Public packages software available on server\n"
        url = options.server+'/post/'
        softxml = uecommunication.get_public_software_list(url, options)
        uecommunication.printable_public_software(softxml)
        
        logging.info("List public packages available on server")
        localtime   = time.localtime()
        logging.info("End: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))
        raw_input("Press Enter to Exit")

    if options.get is not None and options.server is not None:
        logging.info("*********************************\n")
        localtime   = time.localtime()
        logging.info("Start: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))
        
        url = options.server+'/post/'
        print "Will install package Number: %d \n" % options.get
        logging.info("Launch manual install of "+ str(options.get) +" package")
        ue = uedownload()
        ue.download_pack(url, options.get, options)
        
        raw_input("Operation finished, press Enter to Exit")
        localtime   = time.localtime()
        logging.info("End: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))

    if options.inventory is None and options.list is None and options.get is None:
        print "Just to test, inventory will not be send"
        last = True
    
    if options.minute is None:
        last = True

    download = uedownload()

    while True:
        if options.get is not None or options.list is not None:
            break
        logging.info("*********************************\n")
        localtime   = time.localtime()
        logging.info("Start: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))
        
        try:
            inventory = ueinventory.build_inventory()
        except Exception:
            print "Error when building inventory"
            logging.exception("Error when building inventory")
        else:
            if inventory is not None:
                localtime   = time.localtime()
                print time.strftime("%Y-%m-%d-%H:%M:%S", localtime)
                print "Inventory built"
                logging.info("Inventory built")

            if options.verbose is not None:
                print inventory
        
            if options.inventory is not None and options.server is not None:
                url = options.server+'/post/'
        
                try:    
                    response_inventory = uecommunication.send_inventory(url, inventory[0], options)
                except Exception:
                    print "Error on send_inventory process"
                    logging.exception("Error on send_inventory process")
                else:
                    print "Inventory sent to "+url
                    logging.info("Inventory sent to "+url)
                    if options.verbose is not None:
                        print response_inventory
                    try:
                        download.download_action(url, str(response_inventory), options)
                    except Exception:
                        print "Error on download_action function"
                        logging.exception("Error on download_action function")
        
        localtime   = time.localtime()
        logging.info("End: "+ time.strftime("%Y-%m-%d-%H:%M:%S", localtime))
        
        if last:
            break
        else:
            logging.info("Waiting "+str(options.minute)+" minute(s) until next inventory\n")
            wait(options.minute, inventory[1])

if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception("Error in main() function")
