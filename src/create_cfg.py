#!/usr/bin/env python
#
# Copyright (c) 2013 GhostBSD
#
# See COPYING for licence terms.
#
# create_cfg.py v 1.4 Friday, January 17 2014 Eric Turgeon
#

import os
import pickle
from subprocess import Popen, PIPE

# Directory use from the installer.
tmp = "/tmp/.gbi/"
installer = "/usr/local/lib/gbi/"
# Installer data file.
disk = '%sdisk' % tmp
layout = '%slayout' % tmp
model = '%smodel' % tmp
pcinstallcfg = '%spcinstall.cfg' % tmp
user_passwd = '%suser' % tmp
language = '%slanguage' % tmp
dslice = '%sslice' % tmp
left = '%sleft' % tmp
partlabel = '%spartlabel' % tmp
timezone = '%stimezone' % tmp
KBFile = '%skeyboard' % tmp
boot_file = '%sboot' % tmp
disk_schem = '%sscheme' % tmp
zfs_config = '%szfs_config' % tmp
ufs_config = tmp + 'ufs_config'


class gbsd_cfg():
    def __init__(self):
        f = open('%spcinstall.cfg' % tmp, 'w')
        # Installation Mode
        f.writelines('# Installation Mode\n')
        f.writelines('installMode=fresh\n')
        f.writelines('installInteractive=no\n')
        f.writelines('installType=GhostBSD\n')
        f.writelines('installMedium=livecd\n')
        f.writelines('packageType=livecd\n')
        # System Language
        langfile = open(language, 'r')
        lang = langfile.readlines()[0].rstrip()
        f.writelines('\n# System Language\n\n')
        f.writelines('localizeLang=%s\n' % lang)
        os.remove(language)
        # Keyboard Setting
        if os.path.exists(model):
            f.writelines('\n# Keyboard Setting\n')
            os.remove(model)
        if os.path.exists(KBFile):
            rkb = open(KBFile, 'r')
            kb = rkb.readlines()
            kbl = kb[0].rstrip()
            f.writelines('localizeKeyLayout=%s\n' % kbl)
            kbv = kb[1].rstrip()
            if kbv != 'None':
                f.writelines('localizeKeyVariant=%s\n' % kbv)
            kbm = kb[2].rstrip()
            if kbm != 'None':
                f.writelines('localizeKeyModel=%s\n' % kbm)
        # Timezone
        if os.path.exists(timezone):
            time = open(timezone, 'r')
            t_output = time.readlines()[0].strip()
            f.writelines('\n# Timezone\n')
            f.writelines('timeZone=%s\n' % t_output)
            f.writelines('enableNTP=yes\n')
            os.remove(timezone)
        if os.path.exists(zfs_config):
            # Disk Setup
            r = open(zfs_config, 'r')
            zfsconf = r.readlines()
            for line in zfsconf:
                if 'partscheme' in line:
                    f.writelines(line)
                    read = open(boot_file, 'r')
                    boot = read.readlines()[0].strip()
                    if boot == 'refind':
                        f.writelines('bootManager=none\n')
                        f.writelines('efiLoader=%s\n' % boot)
                    else:
                        f.writelines('bootManager=%s\n' % boot)
                        f.writelines('efiLoader=none\n')
                    os.remove(boot_file)
                else:
                    f.writelines(line)
            # os.remove(zfs_config)
        elif os.path.exists(ufs_config):
            # Disk Setup
            r = open(ufs_config, 'r')
            ufsconf = r.readlines()
            for line in ufsconf:
                if 'partscheme' in line:
                    f.writelines(line)
                    read = open(boot_file, 'r')
                    boot = read.readlines()[0].strip()
                    if boot == 'refind':
                        f.writelines('bootManager=none\n')
                        f.writelines('efiLoader=%s\n' % boot)
                    else:
                        f.writelines('bootManager=%s\n' % boot)
                        f.writelines('efiLoader=none\n')
                    os.remove(boot_file)
                else:
                    f.writelines(line)
        else:
            # Disk Setup
            r = open(disk, 'r')
            drive = r.readlines()
            d_output = drive[0].strip()
            f.writelines('\n# Disk Setup\n')
            f.writelines('disk0=%s\n' % d_output)
            os.remove(disk)
            # Partition Slice.
            p = open(dslice, 'r')
            line = p.readlines()
            part = line[0].rstrip()
            f.writelines('partition=%s\n' % part)
            os.remove(dslice)
            # Boot Menu
            read = open(boot_file, 'r')
            line = read.readlines()
            boot = line[0].strip()
            if boot == 'refind':
                f.writelines('bootManager=none\n')
                f.writelines('efiLoader=%s\n' % boot)
            else:
                f.writelines('bootManager=%s\n' % boot)
                f.writelines('efiLoader=none\n')
            # os.remove(boot_file)
            # Sheme sheme
            read = open(disk_schem, 'r')
            shem = read.readlines()[0]
            f.writelines(shem + '\n')
            f.writelines('commitDiskPart\n')
            # os.remove(disk_schem)
            # Partition Setup
            f.writelines('\n# Partition Setup\n')
            part = open(partlabel, 'r')
            # If slice and auto file exist add first partition line.
            # But Swap need to be 0 it will take the rest of the freespace.
            for line in part:
                if 'BOOT' in line or 'BIOS' in line or 'UEFI' in line:
                    pass
                else:
                    f.writelines('disk0-part=%s\n' % line.strip())
            f.writelines('commitDiskLabel\n')
            os.remove(partlabel)
        # Network Configuration
        f.writelines('\n# Network Configuration\n')
        readu = open(user_passwd, 'rb')
        uf = pickle.load(readu)
        net = uf[5]
        f.writelines('hostname=%s\n' % net)
        # Set the root pass
        f.writelines('\n# Network Configuration\n')
        readr = open('%sroot' % tmp, 'rb')
        rf = pickle.load(readr)
        root = rf[0]
        f.writelines('\n# Set the root pass\n')
        f.writelines('rootPass=%s\n' % root)
        # Setup our users
        user = uf[0]
        f.writelines('\n# Setup user\n')
        f.writelines('userName=%s\n' % user)
        name = uf[1]
        f.writelines('userComment=%s\n' % name)
        passwd = uf[2]
        f.writelines('userPass=%s\n' % passwd.rstrip())
        shell = uf[3]
        f.writelines('userShell=%s\n' % shell)
        upath = uf[4]
        f.writelines('userHome=%s\n' % upath.rstrip())
        f.writelines('defaultGroup=wheel\n')
        f.writelines('userGroups=operator\n')
        f.writelines('commitUser\n')
        ifvbox = open('/tmp/.ifvbox', 'w')
        vbguest = Popen('pciconf -lv | grep "VirtualBox Graphics"', shell=True,
                        stdout=PIPE, close_fds=True, universal_newlines=True)
        if "VirtualBox Graphics" in vbguest.stdout.read():
            ifvbox.writelines('True\n')
        else:
            ifvbox.writelines('False\n')
        ifvbox.close()
        f.writelines('runScript=/root/iso_to_hd.sh\n')
        f.writelines('runCommand=rm -f /root/iso_to_hd.sh\n')
        if os.path.exists(zfs_config):
            zfsark = """echo 'vfs.zfs.arc_max="512M"' >> /boot/loader.conf"""
            f.writelines('runCommand=%s\n' % zfsark)
        # adding setting for keyboard in slim
        keyboard_conf = '/usr/local/etc/X11/xorg.conf.d/keyboard.conf'
        k_conf_list = [
            'Section "InputClass"',
            '        Identifier "Keyboard0"',
            '        Driver "kbd"',
            '        Option "XkbLayout"      "%s"' % kbl
        ]
        if kbv != 'None':
            k_conf_list.append('        Option "XkbVariant"     "%s"' % kbv)
        if kbm != 'None':
            k_conf_list.append('        Option "XkbModel"       "%s"' % kbm)
        k_conf_list.append('EndSection')
        for conf_line in k_conf_list:
            if 'Section "InputClass"' == conf_line:
                cmd = """echo '%s' > %s""" % (conf_line, keyboard_conf)
            else:
                cmd = """echo '%s' >> %s""" % (conf_line, keyboard_conf)
            f.writelines('runCommand=%s\n' % cmd)
        f.close()
        os.remove(user_passwd)
