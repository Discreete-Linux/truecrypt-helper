#!/usr/bin/env python
# Encoding: UTF-8
""" A nemo extension which allows force-unmounting of volumes with open
files/references """
import gettext
import sys
import os
import subprocess
import urllib
from gi.repository import GObject, Nemo
import truecrypthelper

class TCUnmountExtension(GObject.GObject, Nemo.MenuProvider):
    """ Allows force-unmounting of volumes """
    def __init__(self):
        """ Init the extionsion. """
        print "Initializing nemo-tc-unmount extension"

    def force_close_activate_cb(self, menu, myfile):
        """ Handle menu activation, i.e. actual umounting """
        mountpoint = myfile.get_mount().get_root().get_path().decode('utf-8', 'replace')
        if not subprocess.call(truecrypthelper.tct + ["-l", mountpoint]):
            tclines = subprocess.Popen(truecrypthelper.tct + ["-l", "-v", mountpoint],
                                       stdout=subprocess.PIPE).communicate()[0].splitlines()
            slot = tclines[0][6:]
            dmname = tclines[2][16:]
            truecrypthelper.tc_force_close(slot, dmname, mountpoint)
        else:
            try:
                subprocess.call(["/bin/umount", "-l", mountpoint])
            except:
                truecrypthelper.show_error(gettext.dgettext('truecrypt-helper',
                                                            "An error occured!") +
                                           '\n' + str(sys.exc_info()))
        return

    def close_activate_cb(self, menu, myfile):
        """ Handle menu activation, i.e. actual umounting """
        mountpoint = myfile.get_mount().get_root().get_path().decode('utf-8', 'replace')
        truecrypthelper.tc_close(mountpoint)
        return

    def is_valid_file(self, myfile):
        """ Check if myfile is a valid file for us """
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
        if not self.is_valid_file(myfile):
            return
        item1 = Nemo.MenuItem(name='Nemo::force_unmount',
                              label=gettext.dgettext('truecrypt-helper',
                                                     'Force-Unmount Container'),
                              tip=gettext.dgettext('truecrypt-helper',
                                                   'Forcibly Unmounts the selected TrueCrypt '
                                                   'Container'))
        item1.connect('activate', self.force_close_activate_cb, myfile)
        item2 = Nemo.MenuItem(name='Nemo::tc_unmount',
                              label=gettext.dgettext('truecrypt-helper', 'Unmount Container'),
                              tip=gettext.dgettext('truecrypt-helper',
                                                   'Unmounts the selected TrueCrypt Container'))
        item2.connect('activate', self.close_activate_cb, myfile)
        return item1, item2,
