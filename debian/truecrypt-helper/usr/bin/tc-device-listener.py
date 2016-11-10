#!/usr/bin/python
# Encoding: UTF-8

import time
import glob
import subprocess
import truecrypthelper
from gi.repository import GObject, Gio

class VCDeviceListener(object):
    def drive_connected(self, obj, data):
        truecrypthelper.drive_connected(data)

    def drive_disconnected(self, obj, data):
        device = data.get_volume().get_identifier("unix-device")
        if device.startswith("/dev/dm-"):
            truecrypthelper.complete_unmount(device, mountpoint)
                    
    def mount_pre_unmount(self, obj, data):
        mountpoint = data.get_root().get_path().rstrip('/')
        device = data.get_volume().get_identifier("unix-device")
        if device.startswith("/dev/dm-"):
            truecrypthelper.complete_unmount(device, mountpoint)

    def __init__(self):
        self.vm = Gio.VolumeMonitor.get()
        for drive in self.vm.get_connected_drives():
            self.drive_connected(None, drive)
        self.vm.connect("drive-connected", self.drive_connected)
        self.vm.connect("drive-disconnected", self.drive_disconnected)
        self.vm.connect("mount-pre-unmount", self.mount_pre_unmount)

if __name__ == "__main__":
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    loop = GObject.MainLoop()
    VCDeviceListener()
    loop.run()
