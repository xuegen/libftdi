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


# bitbang
ret = ftdi.set_bitmode(ftdic, 0xff, ftdi.BITMODE_BITBANG)
if ret < 0:
    print('Cannot enable bitbang')
    os._exit(1)
print('turning everything on')
ftdi.write_data(ftdic, chr(0xff), 1)
time.sleep(1)
print('turning everything off\n')
ftdi.write_data(ftdic, chr(0x00), 1)
time.sleep(1)
for i in range(8):
    data = ftdi.read_data(ftdic, 4)
    print('read {}'.format(data))
    val = 2 ** i
    print('enabling bit #%d (0x%02x)' % (i, val))
    buf = chr(val)
    ftdi.write_data(ftdic, buf, 1)
    time.sleep(1)
ftdi.disable_bitbang(ftdic)
print('')

# read pins
ret, pins = ftdi.read_pins(ftdic)
if (ret == 0):
    if sys.version_info[0] < 3:  # python 2
        pins = ord(pins)
    else:
        pins = pins[0]
    print('pins: 0x%x' % pins)


# read chip id
ret, chipid = ftdi.read_chipid(ftdic)
if (ret == 0):
    print('chip id: 0x%x\n' % (chipid & 0xffffffff))


# read eeprom
for eeprom_addr in range(4):
    ret, eeprom_val = ftdi.read_eeprom_location(ftdic, eeprom_addr)
    if (ret == 0):
        print('eeprom @ %d: 0x%04x\n' % (eeprom_addr, (eeprom_val & 0xffff)))


for tt in range(4):
    ret = ftdi.read_eeprom(ftdic)
    size = 128
    ret, eeprom = ftdi.get_eeprom_buf(ftdic, size)
    if ret < 0:
        print('read_eeprom failed')
        print('%s' % ftdi.get_error_string(ftdic))
        break
    else:
        print('eeprom:')
        for i in range(size):
            octet = eeprom[i]
            if sys.version_info[0] < 3:  # python 2
                octet = ord(octet)
            sys.stdout.write('%02x ' % octet)
            if (i % 8 == 7):
                print('')
    print('')
    if tt == 3:
        break

    if tt == 0:  # write eeprom location
        eeprom_addr = 0xd;
        print('write eeprom location: 0x%x' % eeprom_addr)
        ret = ftdi.write_eeprom_location(ftdic, eeprom_addr, 0xaabb)
        if ret < 0:
            print('write_eeprom_location failed')
            print('%s' % ftdi.get_error_string(ftdic))
        ret, eeprom_val = ftdi.read_eeprom_location(ftdic, eeprom_addr)
        if ret < 0:
            print('read back eeprom location failed')
            print('%s' % ftdi.get_error_string(ftdic))
        else:
            print('read back eeprom: 0x%x' % (eeprom_val & 0xffff))
    else:
        if tt == 1:
            print('build eeprom w/o user_data')
            ftdi.eeprom_build(ftdic, None)
        else:
            print('build eeprom with user_data')
            ftdi.eeprom_build(ftdic, '{0x1a: 0x5, 0x1b: 0x00, 0x1c: 0x4a, 0x1d: 0x58}')

        ret = ftdi.write_eeprom(ftdic)
        if (ret < 0):
            print('write eeprom failed')
            print('%s' % ftdi.get_error_string(ftdic))

# close usb
ret = ftdi.usb_close(ftdic)
if ret < 0:
    print('unable to close ftdi device: %d (%s)' %
          (ret, ftdi.get_error_string(ftdic)))
    os._exit(1)

print ('device closed')
ftdi.free(ftdic)
