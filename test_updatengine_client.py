from py.test import raises
from LinuxDpkg.uecommunication import uecommunication
from LinuxDpkg.ueerrors import UeReadResponse, UeImportError, UeResponseError
from urllib2 import URLError
# functions below returns valid or not valid xml inventory to test
# inventory in real conditions
def xml_valid():
    xml=""" 
    <Inventory>
        <Hostname>DONC-AS-GMR-PT</Hostname>
        <SerialNumber>CNU21632N8</SerialNumber>
        <Manufacturer>Hewlett-Packard</Manufacturer>
        <Product>HP ProBook 4530s</Product>
        <Chassistype>Notebook</Chassistype>
        <Ossum>5a5178f1aedd3ad7f33241971c893839</Ossum>
        <Softsum>d41d8cd98f00b204e9800998ecf8427e</Softsum>
        <Netsum>f5633fc61e3968c09ab01a49da51804f</Netsum>
        <Osdistribution>
            <Name>Ubuntu</Name>
            <Version>12.04 - precise</Version>
            <Arch>x86_64</Arch>
            <Systemdrive>-</Systemdrive>
        </Osdistribution>
        <Software>
            <Name>zlib1g:i386</Name>
            <Version>1:1.2.3.4.dfsg-3ubuntu4</Version>
            <Uninstall>Defined only for Windows hosts</Uninstall>
        </Software>
        <Software>
            <Name>zlib1g-dev</Name>
            <Version>1:1.2.3.4.dfsg-3ubuntu4</Version>
            <Uninstall>Defined only for Windows hosts</Uninstall>
        </Software>
        <Network>
            <Ip>127.0.0.1</Ip>
            <Mask>255.0.0.0</Mask>
            <Mac>00:00:00:00:00:00</Mac>
            </Network>
    </Inventory>
        """
    return xml

def xml_not_valid():
    xml=""" 
    <Inventory>
        <Hostname>DONC-AS-GMR-PT</Hostname>
        <SerialNumber>CNU21632N8</SerialNumber>
        <Manufacturer>Hewlett-Packard</Manufacturer>
        <Product>HP ProBook 4530s</Product>
        <Chassistype>Notebook</Chassistype>
        <Ossum>5a5178f1aedd3ad7f33241971c893839</Ossum>
        <Softsum>d41d8cd98f00b204e9800998ecf8427e</Softsum>
        <Netsum>f5633fc61e3968c09ab01a49da51804f</Netsum>
        <BLABLA>
        <Osdistribution>
            <Name>Ubuntu</Name>
            <Version>12.04 - precise</Version>
            <Arch>x86_64</Arch>
            <Systemdrive>-</Systemdrive>
        </Osdistribution>
        <Software>
            <Name>zlib1g:i386</Name>
            <Version>1:1.2.3.4.dfsg-3ubuntu4</Version>
            <Uninstall>Defined only for Windows hosts</Uninstall>
        </Software>
        <Software>
            <Name>zlib1g-dev</Name>
            <Version>1:1.2.3.4.dfsg-3ubuntu4</Version>
            <Uninstall>Defined only for Windows hosts</Uninstall>
        </Software>
        <Network>
            <Ip>127.0.0.1</Ip>
            <Mask>255.0.0.0</Mask>
            <Mac>00:00:00:00:00:00</Mac>
            </Network>
    </Inventory>
        """
    return xml


# Valid response from server after an inventory without -v option
def response_valid_inventory():
    xml ='''"<?xml version="1.0" encoding="UTF-8"?>
    
    <Response>
    
    
    <Import>Import ok</Import>
    
    
    </Response>


    '''
    return xml

# Class options redifined to simulate options will testing
class Options:
    cert = None
# uecommunication.py tests

def test_uereadresponse():
    ue = uecommunication()
    raises(UeReadResponse, ue.valid_response, "<foo></bar>")

def test_ueimporterror():
    ue = uecommunication()
    raises(UeImportError, ue.valid_response, "<Response><Import>Import not ok</Import></Response>")
    assert ue.valid_response(
            "<Response><Import>Import ok</Import></Response>") ==\
            "<Response><Import>Import ok</Import></Response>"

def test_ueresponseerror():
    ue = uecommunication()
    raises(UeResponseError, ue.valid_response, "<Response><status></status></Response>")

def test_send_valid_inventory():
    ue = uecommunication()
    options = Options()
    assert ue.send_inventory("https://127.0.0.1:1979/post/", str(xml_valid()), options) == '<?xml version="1.0" encoding="UTF-8"?>\n\n<Response>\n\n\n<Import>Import ok</Import>\n\n\n</Response>\n\n'

def test_send_not_valid_inventory():
    ue = uecommunication()
    options = Options()
    raises(UeResponseError, ue.send_inventory,"https://127.0.0.1:1979/post/", str(xml_not_valid()), options)

def test_send_bad_adress():
    ue = uecommunication()
    options = Options()
    raises(URLError,ue.send_inventory, "https://bad_url:1979/post/", str(xml_valid()), options)
