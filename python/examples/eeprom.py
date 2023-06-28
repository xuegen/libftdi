#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python example program.

Complete program to demonstrate the usage
of the swig generated python wrapper

You need to build and install the wrapper first"""

import os
import sys
import ftdi1 as ftdi
import time

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
vendorid = 0
productid = 0
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

# set/modify eeprom data.
if not err:
    print('set eeprom data')
    eeprom_data[0x1a] = 0x4
    eeprom_data[0x1b] = 0
    eeprom_data[0x1c] = 0x4a
    eeprom_data[0x1d] = 0x58
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
