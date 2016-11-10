#!/usr/bin/env python
# Truecrypt Helper Plugin for Nemo
#
# Part of "truecrypt-helper" Package
#
# Copyright 2010-2016 Discreete Linux Team <info@discreete-linux.org>
#
# Portions of the code taken from TortoiseHG nemo extension,
# Copyright 2007 Steve Borho
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2, incorporated herein by reference.
#
# Encoding: UTF-8
""" A nemo extension which allows force-unmounting of volumes with open
files/references """
import gettext
import os
import urllib
import syslog
import subprocess
import sys
from multiprocessing import Process
import truecrypthelper
import pyudev
from gi.repository import GObject, Nemo
from gi.repository import Gtk


syslog.openlog("truecrypt-helper")

class TruecryptHelperExtension(GObject.GObject, Nemo.MenuProvider, Nemo.InfoProvider):
    """ Allows opening arbitrary file types as truecrypt volumes """
    def __init__(self):
        """ Init the extionsion. """
        print "Initializing nemo-truecrypt-helper extension"
        self.scanStack = []

    def _double_fork(self, cmd):
        """ Execute child process with double fork.
        Avoids that child becombes zombie when nemo continues without
        ever waiting for the child """
        args = "import subprocess\nsubprocess.Popen(" +str(cmd) + ")"
        subprocess.Popen(["/usr/bin/python", "-c", args])

    def open_activate_cb(self, menu, myfile):
        """ Handle menu activation, i.e. actual mounting """
        filename = myfile.get_location().get_path().decode('utf-8', 'replace')
        self._double_fork(["/usr/bin/vc-open", filename])
        return

    def check_activate_cb(self, menu, myfile):
        filename = myfile.get_location().get_path().decode('utf-8', 'replace')
        self._double_fork(["/usr/bin/tc-check", filename])
        return

    def wipe_activate_cb(self, menu, folder):
        foldername = folder.get_location().get_path().decode('utf-8', 'replace')
        self._double_fork(["/usr/bin/wipefreespace", foldername])
        return

    def force_close_activate_cb(self, menu, myfile):
        """ Handle menu activation, i.e. actual umounting """
        global tc
        mountpoint = myfile.get_mount().get_root().get_path().decode('utf-8', 'replace')
        if not subprocess.call(truecrypthelper.tct + ["-l", mountpoint]):
            tclines=subprocess.Popen(truecrypthelper.tct + ["-t", "-l", "-v",
                                    mountpoint], stdout=subprocess.PIPE).communicate()[0].splitlines()
            slot=tclines[0][6:]
            dmname=tclines[2][16:]
            truecrypthelper.tc_force_close(slot, dmname, mountpoint)
        else:
            try:
                subprocess.call(["/bin/umount", "-l", mountpoint])
            except:
                truecrypthelper.show_error(gettext.dgettext('truecrypt-helper', "An error occured!") + '\n' + str(sys.exc_info()))
        return

    def close_activate_cb(self, menu, myfile):
        """ Handle menu activation, i.e. actual umounting """
        mountpoint = myfile.get_mount().get_root().get_path().decode('utf-8', 'replace')
        Process(target=subprocess.call, args=(("/usr/bin/tc-close", mountpoint), )).start()
        return

    def is_valid_file(self, myfile):
        """ Check if myfile is a valid file for us """
        # Drive icon on desktop
        if ( ( myfile.get_uri_scheme() == 'file' ) or \
            ( myfile.get_uri_scheme() == 'smb' ) ) and \
            ( not myfile.is_directory() ):
            return True
        else:
            return False

    def is_valid_drive(self, myfile):
        """ Check if myfile is a valid drive for us """
        # Drive icon on desktop
        if (myfile.get_uri_scheme() == 'x-nemo-desktop') and \
            (myfile.get_mime_type() == 'application/x-nemo-link'):
            return True
        # Icon in computer:/// view
        elif myfile.get_uri_scheme() == 'computer':
            return True
        # Drive icon in the side panel
        elif (myfile.get_uri_scheme() == 'file') and \
            (os.path.ismount(urllib.unquote(myfile.get_uri()[7:]))):
            return True
        else:
            return False

    def get_file_items(self, window, files):
        """ Tell nemo whether and when to show the menu """
        if len(files) != 1:
            return
        myfile = files[0]
        isfile = self.is_valid_file(myfile)
        isdrive = self.is_valid_drive(myfile)
        if not isfile and not isdrive:
            return
        menu = Nemo.Menu()
        submenu = Nemo.MenuItem(name='Nemo::truecrypt',
                                label=gettext.dgettext('truecrypt-helper', 'VeraCrypt-Container'),
                                tip=gettext.dgettext('truecrypt-helper', 'Treat this file as a veracrypt container'),
                                icon='truecrypt')
        submenu.set_submenu(menu)
        if isfile:
            item1 = Nemo.MenuItem(name='Nemo::open_with_truecrypt',
                                     label=gettext.dgettext('truecrypt-helper', 'Open'),
                                     tip=gettext.dgettext('truecrypt-helper', 'Tries to open the file as a VeraCrypt container'))
            item1.connect('activate', self.open_activate_cb, myfile)
            item2 = Nemo.MenuItem(name='Nemo::check_truecrypt',
                                    label=gettext.dgettext('truecrypt-helper', 'Check'),
                                    tip=gettext.dgettext('truecrypt-helper', 'Checks the container filesystem'))
            item2.connect('activate', self.check_activate_cb, myfile)
            menu.append_item(item1)
            menu.append_item(item2)
        elif isdrive:
            item1 = Nemo.MenuItem(name='Nemo::tc_unmount',
                                     label=gettext.dgettext('truecrypt-helper', 'Unmount'),
                                     tip=gettext.dgettext('truecrypt-helper', 'Unmounts the selected TrueCrypt/VeraCrypt Container'))
            item1.connect('activate', self.close_activate_cb, myfile)
            item2 = Nemo.MenuItem(name='Nemo::force_unmount',
                                 label=gettext.dgettext('truecrypt-helper', 'Force-Unmount'),
                                 tip=gettext.dgettext('truecrypt-helper', 'Forcibly Unmounts the selected TrueCrypt/VeraCrypt Container'))
            item2.connect('activate', self.force_close_activate_cb, myfile)
            menu.append_item(item1)
            menu.append_item(item2)
        if myfile.get_uri_scheme() == "file":
            item = Nemo.MenuItem(name='Nemo::wipe_free_space',
                                label=gettext.dgettext('truecrypt-helper', 'Wipe free space'),
                                tip=gettext.dgettext('truecrypt-helper', 'Overwrites free space on the current location'))
            item.connect('activate', self.wipe_activate_cb, myfile)
            return item, submenu,
        else:
            return submenu,

    def get_background_items(self, window, folder):
        """ Show 'wipe free space' menu entry """
        if folder.get_uri_scheme() != 'file':
            return
        item = Nemo.MenuItem(name='Nemo::wipe_free_space',
                                label=gettext.dgettext('truecrypt-helper', 'Wipe free space'),
                                tip=gettext.dgettext('truecrypt-helper', 'Overwrites free space on the current location'))
        item.connect('activate', self.wipe_activate_cb, folder)
        return item,

    def get_path_for_vfs_file(self, vfs_file):
        if vfs_file.get_uri_scheme() == 'file':
            path = urllib.unquote(vfs_file.get_uri()[7:])
        elif vfs_file.get_uri_scheme() == 'computer':
            mount = vfs_file.get_mount()
            if mount is not None:
                path = mount.get_root().get_path()
            else:
                path = None
        elif ( vfs_file.get_uri_scheme() == 'x-nemo-desktop' ) and \
        ( vfs_file.get_mime_type() == 'application/x-nemo-link' ):
            path = vfs_file.get_mount().get_root().get_path()
        else:
            path = None
        return path

    def _get_file_status(self, localpath):
        emblem, status = None, None
        if os.path.ismount(localpath) and \
            (not subprocess.call(truecrypthelper.tct + ["-l", localpath])):
            emblem, status = "truecrypt", "normal"
        return emblem, status

    def fileinfo_on_idle(self):
        '''Update emblem and status for files when there is time'''
        if not self.scanStack:
            return False
        try:
            vfs_file = self.scanStack.pop()
            path = self.get_path_for_vfs_file(vfs_file)
            if not path:
                return True
            emblem, status = self._get_file_status(path)
            if emblem is not None:
                vfs_file.add_emblem(emblem)
            if status is not None:
                vfs_file.add_string_attribute('tc_status', status)
        except StandardError, e:
            syslog.syslog(str(e))
        return True

    def update_file_info(self, file):
        '''Queue file for emblem and status update'''
        self.scanStack.append(file)
        if len(self.scanStack) == 1:
            GObject.idle_add(self.fileinfo_on_idle)

