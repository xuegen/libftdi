#!/usr/bin/env python
# -*- coding: utf-8 -*-

# program to set the magic bytes in the eeprom so that it can be 
# recognized by Xilinx tool.
import os
import sys
import ftdi1 as ftdi
import time

modify = 1  # set to 1 to do a modified write after read.
# vendorid and product id to scan for the device.
vendorid = 0x0403
productid = 0x6011

# version
print ('version: %s\n' % ftdi.__version__)

# initialize
ftdic = ftdi.new()
if ftdic == 0:
    print('new failed: %d' % ret)
    os._exit(1)

# try to list ftdi devices 0x6011 or 0x6001
#ret, devlist = ftdi.usb_find_all(ftdic, 0x0403, 0x6011)
#if ret <= 0:
#    ret, devlist = ftdi.usb_find_all(ftdic, 0x0403, 0x6001)

# try to list all ftdi devices
ret, devlist = ftdi.usb_find_all(ftdic, vendorid, productid)

if ret < 0:
    print('ftdi_usb_find_all failed: %d (%s)' %
          (ret, ftdi.get_error_string(ftdic)))
    os._exit(1)
print('devices: %d' % ret)
curnode = devlist
i = 0
while(curnode != None):
    ret, fields = ftdi.usb_get_dev_desc(ftdic, curnode.dev)
    if ret < 0:
        print('ftdi_usb_get_dev_desc failed: %d (%s)' %
              (ret, ftdi.get_error_string(ftdic)))
    print('--------------------------------------')
    print('Device descriptor:')
    for jj in range(ret):
        print('%d %s: 0x%x' % (jj, ftdi.usb_get_dev_desc_fieldname(jj), fields[jj]))
        if vendorid == 0 or productid == 0:
            vendorid = fields[7]
            productid = fields[8]
    print('--------------------------------------')

    ret, manufacturer, description, serial = ftdi.usb_get_strings(
        ftdic, curnode.dev)
    if ret < 0:
        print('ftdi_usb_get_strings failed: %d (%s)' %
              (ret, ftdi.get_error_string(ftdic)))
    else:
        print('#%d: manufacturer="%s" description="%s" serial="%s"\n' %
              (i, manufacturer, description, serial))
    curnode = curnode.next
    i += 1

# open usb
print('open usb vendorid 0x%x, product id 0x%x' % (vendorid, productid))
ret = ftdi.usb_open(ftdic, vendorid, productid)
if ret < 0:
    print('unable to open ftdi device: %d (%s)' %
          (ret, ftdi.get_error_string(ftdic)))
    os._exit(1)


print('read eeprom')
ret = ftdi.read_eeprom(ftdic)
size = 128
eeprom_data = [0]*size
ret, eeprom = ftdi.get_eeprom_buf(ftdic, size)
err = False
if ret < 0:
    print('read_eeprom failed')
    print('%s' % ftdi.get_error_string(ftdic))
    err = True
else:
    print('eeprom:')
    for i in range(size):
        eeprom_data[i] = eeprom[i]
        octet = eeprom[i]
        if sys.version_info[0] < 3:  # python 2
            octet = ord(octet)
        sys.stdout.write('%02x ' % octet)
        if (i % 8 == 7):
            print('')
if modify:
    # set/modify eeprom data.
    if not err:
        print('set eeprom data')
        offset = eeprom_data[0x12] - 0x80 + eeprom_data[0x13]
        eeprom_data[offset] = 0x02
        eeprom_data[offset+1] = 0x03
        eeprom_data[offset+2] = 0x00
        eeprom_data[offset+3] = 0x00
        eeprom_data[offset+4] = 0x4
        eeprom_data[offset+5] = 0
        eeprom_data[offset+6] = 0x4a
        eeprom_data[offset+7] = 0x58
        ftdi.set_eeprom_buf(ftdic, eeprom_data)

    # calculate checksum
    if not err:
        print('calculate checksum')
        ret = ftdi.eeprom_checksum(ftdic)
        if ret < 0:
            print('%s' % ftdi.get_error_string(ftdic))
            err = True

    # write eeprom
    if not err:
        print('write eeprom')
        ret = ftdi.write_eeprom(ftdic)
        if (ret < 0):
            print('write eeprom failed')
            print('%s' % ftdi.get_error_string(ftdic))
            err = True

# close usb
ret = ftdi.usb_close(ftdic)
if ret < 0:
    print('unable to close ftdi device: %d (%s)' %
          (ret, ftdi.get_error_string(ftdic)))
    os._exit(1)

print ('device closed')
ftdi.free(ftdic)
