��    U      �  q   l      0  
   1  P   <  *   �  	   �  U   �       2   *     ]     l     r     �     �  (   �  #   �     	  6   	  5   T	  H   �	  4   �	     
  &   !
     H
  �   c
  ,   �
          '  (   =     f     ~  2   �     �  �   �     �  B   �     �     �  -   �     "     1  A   L     �  4   �  ,   �  )     C   /  1   s  <   �  !   �  V     I   [  n  �       (   (  /   Q     �      �     �     �  )   �  -   �     &     >     N     _  f   n     �     �  2   �  0   $     U  7   p  	   �  �   �     `     h     {     �     �     �  	   �     �     �  
   �     	      
   �  W   �  0   �     #  ;   0     l  D   �     �     �  #   �            1   0  -   b     �  =   �  H   �  c   6  :   �     �  :   �  %   /  �   U  8   �     +     E  8   [  "   �     �  B   �       �   '     �  D   
     O     W  9   u     �     �  L   �     +  1   D  *   v  *   �  @   �  2     O   @  %   �  X   �  u      �  �      "  -   "  6   M"     �"     �"     �"  
   �"  0   �"  =   #     ?#     ]#     q#     �#  o   �#     $     $  E   7$  G   }$  -   �$  ;   �$     /%  �   @%     �%     &     &     *&     9&     L&  	   l&     v&  %   �&  
   �&     �&           5      4       =                        +   L                 
   3   P   ?   >                 &           2   N   "           %   H   K       -   M   <   U                 )   '   R   S          @       7                 !   A   ,      $   F      (   9           	   1   G          .       O   :              I   T   J   /          D   8   Q   B   #              E       C               6         *   0      ;    %s MB max. A backup container already exists at that location. Do you want to overwrite it? All data on the data medium will be lost!
 All files An error occured while trying to execute the wiping programm. The error was
<i>%s</i> An error occured! Are you sure you want to encrypt this data medium? Basic Settings Check Checks the container filesystem Container Selection Container _size: Could not create filesystem on Container Could not find device for Container Could not open Container Could not partition device. The error returned was:
%s Could not remove temp dir. The error returned was:
%s Could not unmount device. Maybe there is an open TrueCrypt volume on it? Could not unmount device. The error returned was:
%i Create a container _file Create a volume for automatic _backups Create an _extended volume Do you really want to stop the wiping process? This may leave data fragments with random names behind, which can be safely deleted. Do you really want to stop volume creation?
 Encryption options Error information: %s Error: Creating TrueCrypt volume failed. Force dangerous repairs Force-Unmount Forcibly Unmounts the selected TrueCrypt Container Generating volume... IMPORTANT: Move the mouse for about a minute as randomly as possible. This enhances the cryptographic strength of the encryption. When you are done with that click "Generate". It may be used now. Listens for USB devices which could be TrueCrypt encrypted devices Open Overwrite existing? Overwrites free space on the current location Password check Scan for TrueCrypt Volumes Scans for already connected but not yet mounted TrueCrypt Volumes So we will continue. The TrueCrypt volume has been successfully created.
 The container will be removed in doing that. The data medium becomes unusable thereby. The password contains unallowed characters. Allowed characters are: The password must be at least %d characters long! The password must contain at least one non-letter character! The process has just terminated.
 There is already another truecrypt-helper process running, please let it finish first. This script does not work with multiple files selected. Please try again. This will overwrite once the free space on the filesystem 
<i>%s</i>
once with random data.

Note that this
a) May still leave small parts of data recoverable due to wear leveling mechanisms
b) May shorten the life of flash media if used extensively.
c) May leave meaningless data files on your drive if cancelled. These can be safely deleted.

Click OK to continue. Too many arguments. Treat this file as a truecrypt container Tries to open the file as a TrueCrypt container TrueCrypt files TrueCrypt helper device listener TrueCrypt-Container Unmount Unmounts the selected TrueCrypt Container Use an entire _data medium for created volume VeraCrypt Volume Wizard Volume Creation Volume Selection Volume _label: WARNING: This enables repair actions which may further corrupt the filesystem if something goes wrong. Wipe free space Wiping done Wiping free space on %s has successfully completed Wiping free space on %s. This may take some time Wiping free space on %s... Wiping was not sucessful. The errorcode returned was %s Wiping... You are about to check and repair a filesystem. Even though this works in most cases, it is advisable to have a backup in case something goes wrong. Do you want to continue? _Browse _Confirm password: _Container file: _Data medium: _Display password _Encryption algorithm: _Generate _Hash algorithm: _Multiple passes (for floppies) _Password: _Stop Project-Id-Version: truecrypt-helper 0.8
Report-Msgid-Bugs-To: info@discreete-linux.org
POT-Creation-Date: 2016-11-02 13:41+0100
PO-Revision-Date: 2016-11-02 13:48+0100
Last-Translator: UPR Team <info@privacy-cd.org>
Language-Team: LANGUAGE <de@li.org>
Language: de
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 1.6.10
 %s MB max. Es existiert bereits ein Backup-Container an diesem Ort. Soll er überschrieben werden? Alle Daten auf dem Datenträger gehen verloren!
 Alle Dateien Ein Systemfehler ist aufgetreten. Der Fehler war

<i>%s</i> Ein Fehler ist aufgetreten Sind Sie sicher, dass Sie diesen Datenträger verschlüsseln wollen? Grundeinstellungen Prüfen Prüft das Dateisystem im Container Container-Auswahl Container-Größe: Konnte kein Dateisystem auf dem Container anlegen Konnte kein Gerät zu diesem Container finden Konnte Container nicht öffnen Konnte das Gerät nicht partitionieren. Der Fehlercode war %s Konnte das temporäre Verzeichnis nicht entfernen. Der Fehlercode war %s Konnte das Gerät nicht aushängen. Möglicherweise ist noch ein TrueCrypt Volume darauf geöffnet? Konnte das Gerät nicht aushängen. Der Fehlercode war:
%i Eine _Container-Datei erzeugen Einen Container für automatische Daten_sicherung erzeugen Einen _erweiterten Container erzeugen Wollen Sie den Überschreib-Vorgang wirklich abbrechen? Dadurch können Datenreste mit Zufallsnamen zurück bleiben, die gefahrlos gelöscht werden können. Wollen Sie wirklich die Erzeugung des Volumens stoppen?
 Verschlüsselungsoptionen Fehlerinformation: %s Fehler: Das Erzeugen des TrueCrypt Volumens schlug fehl. Unsichere Reparaturen durchführen Aushängen erzwingen Den ausgewählten TrueCrypt Container erzwungenermaßen aushängen Volumen wird erzeugt... WICHTIG: Bewegen Sie die Maus für etwa eine Minute so zufällig wie möglich. Das erhöht die kryptografische Stärke der Verschlüsselung. Wenn Sie damit fertig sind, klicken Sie auf "Erzeugen". Es kann jetzt benutzt werden. Sucht nach USB-Geräten, die TrueCrypt-verschlüsselt sein könnten. Öffnen Existierenden überschreiben? Überschreibt freien Speicherplatz am gegenwärtigen Ort. Passwort Prüfung Suche nach TrueCrypt-Volumes Sucht nach bereits angeschlossenen, aber nicht geöffneten TrueCrypt-Volumes Daher wird fortgefahren. Das TrueCrypt Volumen wurde erfolgreich erzeugt.
 Der Container wird dabei wieder gelöscht. Der Datenträger wird dadurch unbenutzbar. Das Passwort enthält ungültige Zeichen. Erlaubte Zeichen sind: Das Passwort muss mindestens %d Zeichen lang sein! Das Passwort muss mindestens ein Zeichen enthalten, welches kein Buchstabe ist! Der Prozess hat sich gerade beendet.
 Es läuft noch ein anderer Truecrypt-Prozess, bitte warten Sie bis er abgeschlossen ist. Dieses Skript funktioniert nicht mit mehreren ausgewählten Dateien. Bitte nur eine auswählen und nochmal versuchen. Hierdurch wird der freie Speicherplatz auf 
<i>%s</i>
einmal überschrieben. Bitte beachten Sie, dass
a) Kleine Reste wiederherstellbarer Daten übrig bleiben können
b) Die Lebensdauer von USB-Sticks bei häufigem Gebrauch abnehmen kann
c) Sinnlose Dateien zurückbleiben können, wenn der Vorgang abgebrochen wird. Diese können gefahrlos gelöscht werden.

Klicken Sie OK zum Fortfahren. Zu viele Parameter Diese Datei als TrueCrypt-Container behandeln Versucht, die Datei als TrueCrypt Container zu öffnen TrueCrypt Dateien TrueCrypt Geräteerkennung TrueCrypt-Container Aushängen Den ausgewählten TrueCrypt Container aushängen Einen ganzen _Datenträger für das erzeugte Volumen benutzen VeraCrypt Container Assistent Container-Erzeugung Container-Auswahl Volumen-Kennung: ACHTUNG: Dies aktiviert Reparaturen, die das Dateisystem im Falle eines Fehlschlags weiter beschädigen können Freien Speicher wipen Überschreiben abgeschlossen Überschreiben des freien Speichers auf %s erfolgreich abgeschlossen. Freier Speicherplatz auf %s wird gelöscht. Das kann lange Zeit dauern. Freier Speicherplatz auf %s wird gelöscht... Überschreiben war nicht erfolgreich. Der Fehlercode war %s Überschreibe... Sie sind dabei, ein Dateisystem zu prüfen und zu reparieren. Auch wenn dies in den meisten Fällen gelingt, sollten sie vorher eine Sicherung angefertigt haben. Wollen Sie fortfahren? _Suchen Passwort_bestätigung: _Container-Datei: _Datenträger: Passwort _anzeigen _Verschlüsselungs-Algorithmus: _Erzeugen _Hash-Algorithmus: _Mehrere Durchgänge (für Disketten) _Passwort: _Stop 