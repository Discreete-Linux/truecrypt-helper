#  PACKAGE
#
#  Copyright (C) 2016 Discreete Linux Team <info@discreete-linux.org>
#
###
# Standard-Variablen, die angepasst werden müssen
PYMODS = truecrypthelper.py
BINFILES =
USRBINFILES = luks-open tc-open tc-close tc-check tc-wizard tc-device-listener.py tc-device-rescan.py wipefreespace vc-open
EXTENSIONS = truecrypt-helper.py
MENUFILES = truecrypt-helper-luks.desktop truecrypt-helper-tc.desktop truecrypt-helper-vc.desktop truecrypt-helper-wizard.desktop tc-device-rescan.desktop
EXTRATARGETS = 
EXTRAINSTALLS = polkit sudo xdgstart
###
# Automatische Variablen
NAME = $(shell grep '^Package: ' debian/control | sed 's/^Package: //')
VERSION = $(shell grep '^Version: ' debian/control | sed 's/^Version: //')
PYTHON_VERSION = $(shell python -V 2>&1 | cut -f 2 -d ' ')
PYMINOR := $(shell echo $(PYTHON_VERSION) | cut -f 2 -d '.')
PYMAJOR := $(shell echo $(PYTHON_VERSION) | cut -f 1 -d '.')
BINDIR = $(DESTDIR)/bin
USRBINDIR = $(DESTDIR)/usr/bin
MENUDIR = $(DESTDIR)/usr/share/applications
ICONDIR = $(DESTDIR)/usr/share/icons/gnome
EXTDIR = $(DESTDIR)/usr/share/nemo-python/extensions
LIBDIR = $(DESTDIR)/usr/lib/$(NAME)
LANGDIR = $(DESTDIR)/usr/share/locale
ifeq ($(PYMAJOR),3)
PYLIBDIR = $(DESTDIR)/usr/lib/python3/dist-packages
else
PYLIBDIR = $(DESTDIR)/usr/lib/python2.$(PYMINOR)/dist-packages
endif
ICONS = $(wildcard icons)
UIFILES = $(wildcard *.ui)
POFILES=$(wildcard *.po)
MOFILES=$(addprefix $(LANGDIR)/,$(POFILES:.po=/LC_MESSAGES/$(NAME).mo))
###
# Weitere lokale Variablen
PKITDIR = $(DESTDIR)/etc/polkit-1/localauthority/50-local.d
SUDODIR = $(DESTDIR)/etc/sudoers.d
XDGSTARTDIR = $(DESTDIR)/etc/xdg/autostart
XDGSTART = tc-device-listener.desktop
PKLA = org.privacy-cd.desktop.pkla
SUDOFILES = truecrypt-helper-sudo
###
# Standard-Rezepte
all:	$(EXTRATARGETS)

clean:
	rm -rf *.pyc

distclean:
	rm -rf *.pyc *.gz $(EXTRATARGETS)
	
$(NAME).pot:	$(BINFILES) $(USRBINFILES) $(UIFILES) $(EXTENSIONS) $(PYLIBS)
	xgettext -L python -d $(NAME) -o $(NAME).pot \
	--package-name=$(NAME) --package-version=$(VERSION) \
	--msgid-bugs-address=info@discreete-linux.org $(BINFILES) $(USRBINFILES) \
	$(EXTENSIONS) $(PYLIBS)
ifneq ($(UIFILES),)
	xgettext -L Glade -d $(NAME) -j -o $(NAME).pot \
	--package-name=$(NAME) --package-version=$(VERSION) \
	--msgid-bugs-address=info@discreete-linux.org $(UIFILES)
endif
ifneq ($(POTEXTRA),)
	cat $(POTEXTRA) >> $(NAME).pot
endif

update-pot:	$(NAME).pot

update-po:	$(NAME).pot
	for pofile in $(POFILES); do msgmerge -U --lang=$${pofile%.*} $$pofile $(NAME).pot; done

man:	$(MANFILES)
ifneq ($(MANFILES),)
	gzip -9 $(MANDIR)/$(MANFILES)
endif

install:	install-bin install-extension install-icon install-lang install-lib install-ui install-usrbin install-usrsbin install-menu $(EXTRAINSTALLS)

install-bin:	$(BINFILES)
ifneq ($(BINFILES),)
	mkdir -p $(BINDIR)
	install -m 0755 $(BINFILES) $(BINDIR)
endif	

install-extension:	$(EXTENSIONS)
ifneq ($(EXTENSIONS),)
	mkdir -p $(EXTDIR)
	install -m 0644 $(EXTENSIONS) $(EXTDIR)
endif
	
install-icon:	$(ICONS)
ifneq ($(ICONS),)
	mkdir -p $(ICONDIR)
	cp -r $(ICONS)/* $(ICONDIR)
endif
	
install-lang:	$(MOFILES)

$(LANGDIR)/%/LC_MESSAGES/$(NAME).mo: %.po
	mkdir -p $(dir $@)
	msgfmt -c -o $@ $*.po	

install-lib:	$(PYMODS)
ifneq ($(PYMODS),)
	mkdir -p $(PYLIBDIR)
	install -m 0644 $(PYMODS) $(PYLIBDIR)	
endif

install-ui:	$(UIFILES)
ifneq ($(UIFILES),)
	mkdir -p $(LIBDIR)
	install -m 0644 $(UIFILES) $(LIBDIR)
endif
	
install-usrbin:	$(USRBINFILES)
ifneq ($(USRBINFILES),)
	mkdir -p $(USRBINDIR)
	install -m 0755 $(USRBINFILES) $(USRBINDIR)
endif

install-usrsbin:	$(USRSBINFILES)
ifneq ($(USRSBINFILES),)
	mkdir -p $(USRSBINDIR)
	install -m 0755 $(USRSBINFILES) $(USRSBINDIR)
endif

install-menu:	$(MENUFILES)
ifneq ($(MENUFILES),)
	mkdir -p $(MENUDIR)
	install -m 0755 $(MENUFILES) $(MENUDIR)
endif
.PHONY:	all clean distclean install

polkit:	$(PKLA)
	mkdir -p $(PKITDIR) && \
	install -m 0644 $(PKLA) $(PKITDIR)

xdgstart:	$(XDGSTART)
	mkdir -p $(XDGSTARTDIR) && \
	install -m 0644 $(XDGSTART) $(XDGSTARTDIR)

sudo:   $(SUDOFILES)
	mkdir -p $(SUDODIR) && \
	install -m 0440 $(SUDOFILES) $(SUDODIR)
	
mime:	$(MIMEFILES)
ifneq ($(MIMEFILES),)
	mkdir -p $(MIMEDIR)
	install -m 0644 $(MIMEFILES) $(MIMEDIR)
endif
