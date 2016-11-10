#!/usr/bin/python
# Encoding: UTF-8
from gi.repository import Gio
import truecrypthelper

if __name__ == "__main__":
    self.vm = Gio.VolumeMonitor.get()
        for drive in vm.get_connected_drives():
            truecrypthelper.drive_connected(drive)
