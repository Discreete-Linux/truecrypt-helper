#!/usr/bin/python
# Encoding: UTF-8
""" Handle opening/closing of TrueCrypt volumes """
import os
import subprocess
import gettext
import traceback
import sys
import time
import re
import syslog
import shutil
import threading
import multiprocessing
import stat
import glob
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Notify, GObject, Gio, GLib, UDisks

gettext.install("truecrypt-helper", unicode=1)
Notify.init("truecrypt-helper")
pyn = Notify.Notification()
pyn.set_urgency(Notify.Urgency.NORMAL)
pyn.set_app_name("truecrypt-helper")
pyn.set_category("device")
pyn.set_hint("transient", GLib.Variant('b', True))
syslog.openlog("truecrypt-helper")

tc = ""
tcargs = ""
if os.path.exists("/usr/bin/veracrypt"):
    vc = ["/usr/bin/veracrypt"]
    vct = ["/usr/bin/veracrypt", "-t"]
    tc = ["/usr/bin/veracrypt", "--truecrypt"]
    tct = ["/usr/bin/veracrypt", "-t", "--truecrypt"]
    devname = "veracrypt"
elif os.path.exists("/usr/local/bin/veracrypt"):
    vc = ["/usr/local/bin/veracrypt"]
    vct = ["/usr/local/bin/veracrypt", "-t"]
    tc = ["/usr/local/bin/veracrypt", "--truecrypt"]
    tct = ["/usr/local/bin/veracrypt", "-t", "--truecrypt"]
    devname = "veracrypt"
elif os.path.exists("/usr/bin/truecrypt"):
    vc = None
    vct = None
    tc = ["/usr/bin/truecrypt"]
    tct = ["/usr/bin/truecrypt", "-t"]
    devname = "truecrypt"
elif os.path.exists("/usr/local/bin/truecrypt"):
    vc = None
    vct = None
    tc = ["/usr/local/bin/truecrypt"]
    tct = ["/usr/local/bin/truecrypt", "-t"]
    devname = "truecrypt"

class DeviceListener(object):
    def drive_connected(self, object, data):
        pass
        
    def drive_disconnected(self, object, data):
        pass
        
    def volume_added(self, object, data):
        pass
        
    def volume_removed(self, object, data):
        pass
        
    def mount_added(self, object, data):
        pass
        
    def mount_changed(self, object, data):
        pass
        
    def mount_pre_unmount(self, object, data):
        pass
        
    def mount_removed(self, object, data):
        pass
        
    def __init__(self):
        self.vm = Gio.VolumeMonitor()
        self.vm.connect("drive-connected", self.drive_connected)
        self.vm.connect("drive-disconnected", self.drive_disconnected)
        self.vm.connect("volume-added", self.volume_added)
        self.vm.connect("volume-removed", self.volume_removed)
        self.vm.connect("mount-added", self.mount_added)
        self.vm.connect("mount-removed", self.mount_removed)
        self.vm.connect("mount-pre-unmount", self.mount_pre_unmount)
        self.vm.connect("mount-changed", self.mount_changed)  

class PBarThread(threading.Thread):
    """ Runs a process in a separate thread and displays a progress bar
    while it is running. """
    def __init__(self, title, message):
        super(PBarThread, self).__init__()
        self._stop = threading.Event()
        self.win = Gtk.Window()
        self.vbox = Gtk.VBox(homogeneous=True, spacing=10)
        self.label = Gtk.Label(label=message)
        self.pbar = Gtk.ProgressBar()
        self.vbox.pack_start(self.label, True, True, 0)
        self.vbox.pack_start(self.pbar, True, True, 0)
        self.win.add(self.vbox)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_border_width(10)
        self.win.set_keep_above(True)
        self.win.set_title(title)

    def run(self):
        self.win.show_all()
        while not self.stopped():
            self.pbar.pulse()
            while Gtk.events_pending():
                Gtk.main_iteration()
            time.sleep(.25)
        self.win.destroy()
        while Gtk.events_pending():
            Gtk.main_iteration()

    def stop(self):
        """ Stop the running thread """
        self._stop.set()

    def stopped(self):
        """ Return True if the thread is stopped """
        return self._stop.isSet()

def _is_truecrypt(device, name):
    """ Check new volumes for possible TrueCrypt volumes """
    if (not is_tc_wizard_running() and
            not (device.startswith("/dev/mapper/") or device.startswith("/dev/dm-"))):
        if _is_backup_device(device):
            if ask_open_container(name, device, True):
                if vc:
                    tc_open(device, mode="vc")
                else:
                    tc_open(device, mode="tc")
        else:
            if ask_open_container(name, device):
                if vc:
                    tc_open(device, mode="vc")
                else:
                    tc_open(device, mode="tc")

def drive_connected(drive):
    if not drive.has_media():
        return 
    voltype = None
    device = drive.get_identifier("unix-device")
    partitions = glob.glob("%s?" % device)
    if len(partitions) == 0:
        try:
            block_proxy = UDisks.BlockProxy.new_for_bus_sync(Gio.BusType(1), 0, "org.freedesktop.UDisks2", "/org/freedesktop/UDisks2/block_devices/" + device.rsplit('/', 1)[1], None)
            voltype = block_proxy.props.id_type
            #voltype = subprocess.Popen(["/usr/bin/sudo", "/sbin/blkid", "-c",
            #                            "/dev/null", "-s", "TYPE", "-o", "value",
            #                            device],
            #                           stdout=subprocess.PIPE).communicate()[0]
        except:
            pass
        if voltype == "":
            _is_truecrypt(device, drive.get_name())
        elif voltype == "crypto_LUKS":
            luks_open_volume(device)
    else:
        for part in partitions:
            try:
                block_proxy = UDisks.BlockProxy.new_for_bus_sync(Gio.BusType(1), 0, "org.freedesktop.UDisks2", "/org/freedesktop/UDisks2/block_devices/" + part.rsplit('/', 1)[1], None)
                voltype = block_proxy.props.id_type
                #voltype = subprocess.Popen(["/usr/bin/sudo", "/sbin/blkid", "-c",
                #                            "/dev/null", "-s", "TYPE", "-o", "value",
                #                            part],
                #                           stdout=subprocess.PIPE).communicate()[0]
            except:
                pass
            if voltype == "":
                _is_truecrypt(part, drive.get_name())
            elif voltype == "crypto_LUKS":
                luks_open_volume(part)

def start_with_pbar(args, title, message):
    """ Start the process, showing a progress bar. """
    win = Gtk.Window()
    vbox = Gtk.VBox(homogeneous=True, spacing=10)
    label = Gtk.Label(label=message)
    pbar = Gtk.ProgressBar()
    vbox.pack_start(label, True, True, 0)
    vbox.pack_start(pbar, True, True, 0)
    win.add(vbox)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.set_border_width(10)
    win.set_keep_above(True)
    win.set_title(title)
    win.show_all()
    p = multiprocessing.Process(target=subprocess.call, args=(args, ))
    p.start()
    while p.is_alive():
        pbar.pulse()
        while Gtk.events_pending():
            Gtk.main_iteration()
        time.sleep(.25)
    win.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    p.join()
    return p.exitcode

def ask_open_container(name, devfile, backup=False):
    """ Ask the user if he wants to open a TC device """
    question = Gtk.Dialog(buttons=(_("Check filesystem"), 3,
                                   Gtk.STOCK_NO, Gtk.ResponseType.NO,
                                   Gtk.STOCK_YES, Gtk.ResponseType.YES))
    devtext = _("%(name)s (%(device)s) is possibly a truecrypt or veracrypt "
                "encrypted device.\n") % {"name":name, "device":devfile}
    bkuptext = _("%(name)s (%(device)s) is a truecrypt or veracrypt"
                 "encrypted backup device.\n") % {"name":name, "device":devfile}
    questiontext = _("Shall we try to open it?")
    if vc:
        vctext = _("NOTE: We will try to open this as a veracrypt volume "
                   "by default.\nIf you know this is a truecrypt volume "
                   "instead, please check \"TrueCrypt mode\" in the next "
                   "dialog.")
    if backup:
        message = (bkuptext + questiontext)
    else:
        message = (devtext + questiontext)
    if vc:
        message = (message + '\n\n' + vctext)
    label1 = Gtk.Label()
    label1.set_markup(_(message))
    label1.set_line_wrap(False)
    img = Gtk.Image()
    img.set_from_icon_name("truecrypt", Gtk.IconSize.DIALOG)
    hbox = Gtk.HBox()
    hbox.pack_start(img, False, False, 10)
    hbox.pack_start(label1, True, True, 10)
    question.set_title(_("CryptoBox device detected"))
    question.get_content_area().pack_start(hbox, True, True, 10)
    question.set_default_response(Gtk.ResponseType.YES)
    question.set_position(Gtk.WindowPosition.CENTER)
    question.set_urgency_hint(True)
    question.set_keep_above(True)
    question.show_all()
    question.present()
    response = question.run()
    question.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    if response == Gtk.ResponseType.YES:
        return True
    elif response == 3:
        tc_check(devfile)
        return False
    else:
        return False

def show_error(message=None, variables=None):
    """ Display error messages """
    if message is None:
        syslog.syslog("Error: %s; Vars: %s" %
                      (traceback.format_exc(), str(variables)))
        message = _("A system error occured. The error was\n\n%(error)s"
                    "\n\nLocal variables:\n%(vars)s") \
            % {"error":traceback.format_exc(), "vars":str(variables)}
    else:
        syslog.syslog(message.encode('ascii', 'replace'))
    dlg = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK)
    dlg.format_secondary_text(message)
    dlg.run()
    dlg.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    return

def ask_user(title, message):
    """ Ask the user a question with a dialog box. """
    question = Gtk.MessageDialog(buttons=Gtk.ButtonsType.YES_NO,
                                 type=Gtk.MessageType.QUESTION)
    question.set_markup(_(message))
    question.set_title(title)
    question.set_default_response(Gtk.ResponseType.YES)
    question.set_urgency_hint(True)
    question.set_keep_above(True)
    response = question.run()
    question.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    if response == Gtk.ResponseType.YES:
        return True
    else:
        return False

def is_single_instance():
    """ Return true if there is no other instance of tc-helper programs running. """
    proclist = "tc-open tc-close tc-check tc-convert tc-wizard"
    pids = subprocess.Popen(["/bin/ps", "--no-headers", "-o", "pid", "-C",
                             proclist], stdout=subprocess.PIPE).communicate()[0]
    for pid in pids.split():
        if int(pid) != os.getpid():
            return False
    return True

def is_tc_wizard_running():
    """ Return true if the tc-wizard is running. """
    pids = subprocess.Popen(["/bin/ps", "--no-headers", "-o", "pid", "-C",
                             "tc-wizard,gparted,palimpsest"],
                            stdout=subprocess.PIPE).communicate()[0]
    if pids:
        return True
    else:
        return False

def _is_backup_device(device):
    args = [ "/usr/bin/sudo", "/usr/bin/tc-backup-signature", device ]
    prog = subprocess.Popen(args)
    ret = prog.wait()
    return ret == 0

def tc_open(filename, extramountopts=None, mode="vc"):
    """ Open the volume """
    global pyn
    if mode == "vc":
        if not vc:
            show_error(_("VeraCrypt is not installed, cannot open this"
                         "volume in VeraCrypt mode."))
            return
        else:
            app = vc
            appt = vct
    else:
        app = tc
        appt = tct
    if is_tc_wizard_running():
    # silently return False if tc-wizard is running since its partitioning
    # shall not trigger an error message
        return
    if not is_single_instance():
        show_error(_("There is already another truecrypt-helper process "
                     "running, please let it finish first."))
        return
    syslog.syslog(syslog.LOG_DEBUG, "Opening CryptoBox volume %s" %
                  filename.encode('ascii', 'replace'))
    mountopts = ["noexec", "nosuid", "nodev"]
    if extramountopts:
        mountopts.append(extramountopts)

    # find free slot, work around rare truecrypt bug where dm-mappings are
    # not removed
    slot = 1
    while os.path.exists("/dev/mapper/" + devname + str(slot)):
        slot += 1
    # open the volume without mounting it already
    # and extract several variables from TC output.
    try:
        subprocess.check_call(app + ["--filesystem=none", "--load-preferences",
                               "--protect-hidden=no", "--slot="+ str(slot),
                               filename])
        tclines = subprocess.Popen(appt + ["-l", "-v", filename],
                                   stdout=subprocess.PIPE).communicate()[0].splitlines()
    except OSError:
        show_error(variables=vars())
        return
    except subprocess.CalledProcessError:
        syslog.syslog(syslog.LOG_DEBUG, "User cancelled")
        return
    pyn.update(_("Opening CryptoBox volume"),
               _("CryptoBox Volume is being opened, please wait..."),
               "usbpendrive_unmount")
    pyn.show()
    dmname = tclines[2][16:]
    # Get filesystem type and do some checks
    # Label volume according to container file name
    try:
        tcfs = subprocess.Popen(["/usr/bin/sudo", "/sbin/blkid", "-c",
                                 "/dev/null", "-s", "TYPE", "-o", "value",
                                 dmname],
                                stdout=subprocess.PIPE).communicate()[0].splitlines()[0]
    except:
        show_error(_("Failed to detect a valid filesystem on %s. "
                     "The volume may be damaged or unformatted.") % dmname)
        subprocess.call(appt + ["-d", "--slot=%d" %
                         int(dmname.replace("/dev/mapper/" + devname, ""))])
        return
    if not filename.startswith("/dev/"):
        fslabel = os.path.splitext(os.path.basename(filename))[0]
        syslog.syslog(syslog.LOG_DEBUG, "Setting volume label")
        if tcfs == "vfat":
            fslabel = filter(lambda c: c.isalnum() or c in "-_ ", fslabel).upper()[0:10]
            subprocess.call(["/usr/bin/sudo", "/sbin/dosfslabel", dmname, fslabel])
            subprocess.call(["/usr/bin/sudo", "/usr/bin/mlabel", "-i", dmname, "::%s" % fslabel])
        elif tcfs == "ntfs":
            fslabel = fslabel[0:32]
            subprocess.call(["/usr/bin/sudo", "/usr/sbin/ntfslabel", "-q", dmname, fslabel])
        elif tcfs == "exfat":
            fslabel = fslabel[0:15]
            subprocess.call(["/usr/bin/sudo", "/sbin/exfatlabel", dmname, fslabel])
        if "ext" in tcfs:
            fslabel = fslabel[0:15]
            subprocess.call(["/usr/bin/sudo", "/sbin/tune2fs", "-m", "0", "-L", fslabel, dmname])
            syslog.syslog(syslog.LOG_DEBUG, "Doing fsck")
            pyn.update(_("Checking filesystem"),
                       _("Doing a quick filesystem check on %s") %
                       filename, "usbpendrive_unmount")
            pyn.show()
            ret = start_with_pbar(["/usr/bin/sudo", "/sbin/fsck", "-p",
                                   dmname],
                                  _("Checking filesystem on %s...") % dmname,
                                  _("The filesystem on %s is being "
                                    "checked and, if neccessary, repaired.\n"
                                    "This may take a while, please be patient.") % dmname)
            if ret <> 0:
                syslog.syslog(syslog.LOG_WARNING, "fsck failed!")
                show_error(_("Filesystem check on %s failed. "
                             "Try to check and repair the volume.") % filename)
                subprocess.call(appt + ["-d", dmname])
                return False
    if tcfs == "vfat":
        mountopts.append("umask=000")
    try:
    # Mount the volume using udisks
        syslog.syslog(syslog.LOG_DEBUG, "Mounting the volume")
        tempvar = subprocess.Popen(["/usr/bin/udisksctl", "mount",
                                    "--no-user-interaction", "--block-device",
                                    dmname, "--options", ','.join(mountopts)],
                                   stdout=subprocess.PIPE).communicate()[0] \
                                   .decode('utf-8', 'replace')
        mountpoint = re.findall("Mounted /dev/dm[-_a-zA-Z0-9]+ at (.*)", tempvar)[0].rstrip('.')
    except:
        if tempvar.startswith("Mount failed:"):
            show_error(_("Failed to mount the volume. Try to check and repair "
                         "the volume."))
        else:
            show_error(variables=vars())
        subprocess.call(appt + ["-d", "--slot=%d" %
                         int(dmname.replace("/dev/mapper/" + devname, ""))])
        return

    # If this is an ext-formatted volume, make it readable by the current
    # user
    if "ext" in tcfs:
        syslog.syslog(syslog.LOG_DEBUG, "Setting permissions")
        try:
            subprocess.check_call(["/usr/bin/sudo", "/bin/chown", "-R",
                                   "%i:%i" % (os.getuid(), os.getgid()),
                                   mountpoint])
        except OSError:
            show_error(variables=vars())
        except:
            pass

    pyn.update(_("Opening successful"),
               _("CryptoBox volume %s was opened successfully") % filename,
               "usbpendrive_unmount")
    pyn.show()

def tc_force_close(slot, tcdev, tcmp=None):
    """ Forcible close an open TrueCrypt volume """
    global tc
    syslog.syslog("Force-closing TC volume %s" % tcdev.encode('ascii', 'replace'))
    try:
        args = tct + ["-d", "-f", "--slot=" + slot]
        syslog.syslog("Executing " + str(args))
        subprocess.call(args)
    except subprocess.CalledProcessError, err:
        syslog.syslog("Command " + str(args) + " returned error " + str(err))
        sys.exc_clear()
    if os.path.exists(tcmp):
        try:
            args = ["/usr/bin/sudo", "/bin/umount", "-l", tcmp]
            syslog.syslog("Executing " + str(args))
            subprocess.call(args)
        except OSError, err:
            syslog.syslog("Command " + str(args) + " returned error " + str(err))
            sys.exc_clear()
        except:
            syslog.syslog("Exception occured during " + str(args) + ': ' + str(sys.exc_info()))
        time.sleep(3)
        try:
            syslog.syslog("Removing mountpoint")
            args = ["/usr/bin/sudo", "/bin/rmdir", tcmp]
            subprocess.call(args)
        except OSError, err:
            syslog.syslog("Command " + str(args) + " returned error " + str(err))
            sys.exc_clear()
        except:
            syslog.syslog("Exception occured during " + str(args) + ': ' + str(sys.exc_info()))
        time.sleep(3)
        try:
            args = tct + ["-d", "-f", "--slot=" + slot]
            syslog.syslog("Executing " + str(args))
            subprocess.call(args)
        except OSError, err:
            syslog.syslog("Command " + str(args) + " returned error " + str(err))
            sys.exc_clear()
        except:
            syslog.syslog("Exception occured during " + str(args) + ': ' + str(sys.exc_info()))
    if os.path.exists(tcdev) or os.path.exists(tcmp):
        show_error("Closing was only partially successful. "
                   "You should reboot your machine as soon as possible "
                   "to avoid problems.")

def complete_unmount(device, mountpoint):
    global pyn, tc
    dm_device = os.path.basename(device)
    for link in glob.glob("/dev/mapper/%s*" % devname):
        if os.path.basename(os.readlink(link)) == dm_device:
            syslog.syslog(syslog.LOG_DEBUG, "Closing container at %s" %
                  mountpoint.encode('ascii', 'replace'))
            pyn.update(_("Closing CryptoBox volume"),
               _("CryptoBox volume is being closed, please wait..."),
               "usbpendrive_unmount")
            try:
                subprocess.check_call(tct + ["-d", "--slot=%d" %
                                       int(link.replace("/dev/mapper/" + devname, ""))])
                time.sleep(1)
                if os.path.exists(mountpoint):
                    try:
                        os.rmdir(mountpoint)
                    except:
                        pass
            except:
                show_error(variables=vars())
                return False
            pyn.update(_("Closing done"), "", "usbpendrive_unmount")
            pyn.show()
            break

def tc_close(mountpoint):
    """ Close an open TrueCrypt volume """
    global pyn, tc
    if not is_single_instance():
        show_error(_("There is already another truecrypt-helper process running, "
                     "please let it finish first."))
        return
    mountpoint = mountpoint.rstrip('/')
    syslog.syslog(syslog.LOG_DEBUG, "Closing container at %s" %
                  mountpoint.encode('ascii', 'replace'))
    pyn.update(_("Closing CryptoBox volume"),
               _("CryptoBox volume is being closed, please wait..."),
               "usbpendrive_unmount")
    pyn.show()
    if not os.path.ismount(mountpoint):
        show_error(_("Specified mountpoint does not exist (anymore?)"))
        return

    # see if mountpoint is an open tc volume
    if subprocess.call(tct + ["-l", mountpoint],
                       stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT):
        show_error(_("There is no CryptoBox volume mounted at %s.") % mountpoint)
        return

    # Get File and device name of mounted container
    try:
        tclines = subprocess.Popen(tct + ["-l", "-v", mountpoint],
                                   stdout=subprocess.PIPE).communicate()[0]. \
                                   splitlines()
    except subprocess.CalledProcessError:
        return
    except:
        show_error(variables=vars())
        return
    dmname = tclines[2][16:]
    # check for open files
    syslog.syslog(syslog.LOG_DEBUG, "Looking for open files")
    openfiles = subprocess.Popen(["/usr/bin/sudo", "/usr/bin/lsof", "-w",
                                  mountpoint],
                                 stdout=subprocess.PIPE).communicate()[0]
    if len(openfiles) > 0:
        openfileslist = ""
        smbclients = ""
        message = ""
        for line in openfiles.splitlines()[1:]:
            openfileslist += (line.split(None, 8)[8].decode('utf-8', 'replace') + "\n")
        if len(openfileslist) > 0:
            message += ("<b>" + _("There are still open files on %s, listed below. "
                                  "Please close them first.\n\n") % mountpoint +
                        "</b>" + openfileslist + "\n")
        show_error(message)
        return
    trashpath = "%s/.Trash-%i" % (mountpoint, int(os.getuid()))
    if os.path.exists(trashpath):
        if ask_user(_("Empty trash"),
                    _("There are items in the trash on %s. Do you want to empty "
                      "the trash before unmounting?") % mountpoint):
            shutil.rmtree(trashpath, True)
    syslog.syslog(syslog.LOG_DEBUG, "Unmounting and closing container")
    try:
        subprocess.call(["/usr/bin/sudo", "/bin/umount", "-i", mountpoint])
        subprocess.check_call(tct + ["-d", "--slot=%d" %
                               int(dmname.replace("/dev/mapper/" + devname, ""))])
        time.sleep(1)
        if os.path.exists(mountpoint):
            try:
                os.rmdir(mountpoint)
            except:
                pass
    except:
        show_error(variables=vars())
        return
    pyn.update(_("Closing done"), "", "usbpendrive_unmount")
    pyn.show()

def _check_combo_changed(combo, warnlabel):
    a = combo.get_active()
    if a == 0:
        warnlabel.hide()
    elif a == 1:
        warnlabel.set_markup("<span foreground=\"red\">" +
                             _("WARNING: This enables repair actions which may "
                               "further corrupt the filesystem if something goes "
                               "wrong.") + "</span>")
        warnlabel.show()
    else:
        warnlabel.set_markup("<span foreground=\"red\">" +
                             _("WARNING: This will open a terminal where you can "
                               "continue the repair process yourself. Be sure you "
                               "know what you are doing.") + "</span>")
        warnlabel.show()

def _copy_device(filename):
    ret = subprocess.check_call(['/usr/bin/sudo', '/usr/bin/imagewriter-ng',
                                 '-s', filename.rstrip('1234567890')])
    print "Ret = %i" % ret
    return not ret

def tc_check(filename):
    """ Open a truecrypt container and check the filesystem within """
    global tc
    if not is_single_instance():
        show_error(_("There is already another truecrypt-helper process running, "
                     "please let it finish first."))
        return False
    dlg = Gtk.MessageDialog(buttons=Gtk.ButtonsType.YES_NO, type=Gtk.MessageType.QUESTION,
                            message_format=_("You are about to check and repair a "
                                             "filesystem. Even though this works in "
                                             "most cases, it is advisable to have a "
                                             "backup in case something goes wrong. "
                                             "Do you want to continue?"))
    dlg.set_default_response(Gtk.ResponseType.YES)
    dlg.set_keep_above(True)
    dlg.set_urgency_hint(True)
    dlg.set_position(Gtk.WindowPosition.CENTER)
    vbox = Gtk.VBox()
    combo = Gtk.ComboBoxText()
    combo.append_text(_("Normal"))
    combo.append_text(_("Force dangerous repairs"))
    combo.append_text(_("Interactive repair"))
    combo.set_active(0)
    label = Gtk.Label(label=_("Mode of operation:"))
    label.set_alignment(0.0, 0.5)
    hbox = Gtk.HBox()
    warnlabel = Gtk.Label()
    warnlabel.set_line_wrap(True)
    warnlabel.set_alignment(0.0, 0.5)
    warnlabel.set_no_show_all(True)
    hbox.pack_start(label, False, False, 0)
    hbox.pack_start(combo, False, False, 10)
    vbox.pack_start(hbox, False, False, 0)
    vbox.pack_start(warnlabel, False, False, 10)
    combo.connect('changed', _check_combo_changed, warnlabel)
    dlg.get_content_area().pack_start(vbox, True, True, 0)
    dlg.show_all()
    response = dlg.run()
    mode = combo.get_active()
    dlg.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    if response == Gtk.ResponseType.NO:
        return False
    if mode == 1 and stat.S_ISBLK(os.stat(filename)[stat.ST_MODE]):
        if ask_user(_("Make a copy"),
                    _("It is recommended to make a copy of your device before doing "
                      "this. Do you want to make a copy now? Insert an empty "
                      "destination drive before clicking \"Yes\"")):
            if not _copy_device(filename):
                return False
    syslog.syslog(syslog.LOG_DEBUG, "Opening and checking %s" % filename.encode('ascii', 'replace'))
    # find free slot, work around rare truecrypt bug where dm-mappings are
    # not removed
    slot = 1
    while os.path.exists("/dev/mapper/" + devname + str(slot)):
        slot += 1
    # open the volume without mounting it already
    # and extract several variables from TC output.
    try:
        subprocess.check_call(tc + ["--filesystem=none", "--load-preferences",
                               "--protect-hidden=no", "--slot="+ str(slot), filename])
        tclines = subprocess.Popen(tct + ["-l", "-v", filename],
                                   stdout=subprocess.PIPE).communicate()[0].splitlines()
    except OSError:
        show_error(variables=vars())
        return False
    except subprocess.CalledProcessError:
        return False
    encfile = tclines[1][8:]
    dmname = tclines[2][16:]
    if mode == 0:
        args = ["/usr/bin/sudo", "/sbin/fsck", "-f", "-a", dmname]
    elif mode == 1:
        args = ["/usr/bin/sudo", "/sbin/fsck", "-f", "-y", dmname]
    else:
        tcfs = subprocess.Popen(["/usr/bin/sudo", "/sbin/blkid", "-c", "/dev/null",
                                 "-s", "TYPE", "-o", "value", dmname],
                                stdout=subprocess.PIPE).communicate()[0].splitlines()[0]
        if tcfs == "vfat":
            args = ["/usr/bin/xterm", "-T", _("Filesystem check"), "-e", "/bin/rbash",
                    "-c", "sudo dosfsck -wr " + dmname +
                    "; read -p 'Press any key to continue' -n 1 -s"]
        else:
            args = ["/usr/bin/xterm", "-T", _("Filesystem check"), "-e", "/bin/rbash",
                    "-c", "sudo fsck -f " + dmname +
                    "; read -p 'Press any key to continue' -n 1 -s"]
    syslog.syslog(syslog.LOG_DEBUG, "Starting fsck with mode %i..." % mode)
    if mode < 2:
        ret = start_with_pbar(args, _("Checking filesystem on %s...") % dmname,
                              _("The filesystem on %s is being checked and, if neccessary, "
                                "repaired.\nThis may take a while, please be patient.") % dmname)
        syslog.syslog(syslog.LOG_DEBUG, "...fsck returned %i" % ret)
        if ret == 0:
            dlg = Gtk.MessageDialog(type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK)
            dlg.set_markup(_("No errors were found during this check."))
            dlg.run()
            dlg.destroy()
            while Gtk.events_pending():
                Gtk.main_iteration()
        elif ret == 1:
            show_error(_("Errors were found and repaired during this check."))
        else:
            show_error(_("For some reason, filesystem check was not successful or "
                         "did not complete."))
    else:
        ret = subprocess.call(args)
    subprocess.call(tct + ["-d", encfile])

def luks_open_container(filename):
    try:
        fd = os.open(filename, os.O_RDWR)
        mgr = UDisks.ManagerProxy.new_for_bus_sync(Gio.BusType(1), 0, "org.freedesktop.UDisks2", "/org/freedesktop/UDisks2/Manager", None)
        loop_object_path = mgr.call_loop_setup_sync(GLib.Variant('h', 0), GLib.Variant('a{sv}', []), Gio.UnixFDList.new_from_array([fd]), None)[0]
        loop_proxy = UDisks.LoopProxy.new_for_bus_sync(Gio.BusType(1), 0, "org.freedesktop.UDisks2", loop_object_path, None)
        block_proxy = UDisks.BlockProxy.new_for_bus_sync(Gio.BusType(1), 0, "org.freedesktop.UDisks2", loop_object_path, None)
        if block_proxy.props.id_usage != 'crypto':
            loop_proxy.call_set_autoclear_sync(True, GLib.Variant('a{sv}', []), None)
            show_error(_("The file %s does not seem to be a LUKS encrypted container file!") % filename)
    except:
        show_error(_("Unknown error occured while trying to open the LUKS container %s") % filename)
        
def luks_open_volume(device):
    mo = Gtk.MountOperation()
    vm = Gio.VolumeMonitor.get()
    loop = GObject.MainLoop()
    for d in vm.get_connected_drives():
        if d.has_volumes():
            for v in d.get_volumes(): 
                if v.get_identifier('unix-device') == device:
                    v.mount(0, mo, None, luks_open_volume_cb, loop)
                    loop.run()
                    break
        
def luks_open_volume_cb(obj, res, data):
    obj.mount_finish(res)
    syslog.syslog(syslog.LOG_DEBUG, "Successfully mounted LUKS volume at %s" % obj.get_mount().get_root().get_path())
    data.quit()
    
if __name__ == "__main__":
    print "This module cannot be called directly"
