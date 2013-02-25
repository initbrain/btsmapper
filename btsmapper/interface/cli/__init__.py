#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib

import_error = ''

import os
import sys
import re
import gtk.gdk
import subprocess
from time import sleep, strftime, localtime
from commands import getoutput

from btsmapper.core.constants import BTSMAPPER_PATH

def msgbox(message, type_msg=0):
    about = gtk.MessageDialog(None,
                              gtk.DIALOG_MODAL,
                              gtk.MESSAGE_WARNING if type_msg else gtk.MESSAGE_INFO,
                              gtk.BUTTONS_OK,
                              message)
    about.run() # Affichage de la boite de message
    about.destroy() # Destruction de la boite de message

os.system("clear")
print "[+] Vérification de la présence du téléphone"
resIdentify = getoutput("gammu --identify")
if "n'existe pas" in resIdentify:
    gtk.gdk.threads_enter()
    msgbox("Le Nokia n'est plus détecté !", 1)
    gtk.gdk.threads_leave()
else:
    gammuProcess=subprocess.Popen(("gammu", "--config", "%s/core/gammurc" % BTSMAPPER_PATH, "--nokiadebug", "%s/core/nhm5_587.txt" % BTSMAPPER_PATH, "v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print "[+] Subprocess launched (pid=%s)" % gammuProcess.pid

    operateur =	{# Grèce
                    "20201":"COSMOTE",
                    "20205":"GR PANAFON",
                    "20210":"GR HSTET",
                    # Pays-Bas
                    "20404":"NL LIBERTEL",
                    "20408":"NL KPN",
                    "20412":"NL TELFORT",
                    "20416":"Ben NL",
                    "20420":"NL DUTCHTONE",
                    # Belgique
                    "20601":"BEL PROXIMUS",
                    "20610":"B mobistar",
                    "20620":"BASE",
                    # France
                    "20801":"Orange",
                    "20802":"Orange",
                    "20805":"Globalstar Europe",
                    "20806":"Globalstar Europe",
                    "20807":"Globalstar Europe",
                    "20809":"SFR",
                    "20810":"SFR",
                    "20811":"SFR",
                    "20813":"SFR",
                    "20814":"RFF",
                    "20815":"Free Mobile",
                    "20820":"Bouygues Télécom",
                    "20821":"Bouygues Télécom",
                    # Andorre
                    "21303":"AND M-AND",
                    # Espagne
                    "21401":"E AIRTEL",
                    "21402":"MOVISTAR",
                    "21403":"E AMENA",
                    "21407":"MOVISTAR",
                    # Suisse
                    "22801":"Swisscom",
                    "22802":"Sunrise Suisse",
                    "22803":"Orange CH",
                    # Autres
                    "34001":"Orange Caraibe",
                    "64700":"Orange Réunion"}

    try:
        while True:
            out=gammuProcess.stdout.readline().rstrip('\n')
            # print out

            if not out and gammuProcess.poll() != None:
                break

            if "Warning" in out or "Erreur" in out:
                print "[!] "+out
                if "verrouillé" in out: #TODO À vérifier avec un output anglais
                    print "[!] Killing gammu process"
                    os.system("killall gammu")
                    gammuProcess=subprocess.Popen(("gammu", "--config", "%s/core/gammurc" % BTSMAPPER_PATH, "--nokiadebug", "%s/core/nhm5_587.txt" % BTSMAPPER_PATH, "v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print "[+] Subprocess relaunched"
                    print "[+] Please wait 3 seconds"
                    sleep(3)

            elif "Inform : [06 19" in out: # SYSTEM INFORMATION TYPE 1
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            elif "Inform : [06 1a" in out: # SYSTEM INFORMATION TYPE 2
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            elif "Inform : [06 1b" in out: # SYSTEM INFORMATION TYPE 3
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out, '\n'
                out=re.search("Inform : \[([\d\w ]*)\]", out, re.MULTILINE).groups()[0]
                cid="".join(out.split()[2:4])
                mcc="".join(x[::-1].replace("f","") for x in out.split()[4:6])
                mnc=out.split()[6]
                lac="".join(out.split()[7:9])
                out = "\033[0;0m%s \033[22;31m%s \033[22;32m%s \033[01;34m%s \033[22;31m%s \033[0;0m%s" % (' '.join(out.split()[0:2]), ' '.join(out.split()[2:4]), ' '.join(out.split()[4:6]), ' '.join(out.split()[6]), ' '.join(out.split()[7:9]), ' '.join(out.split()[9:]))
                print "[%s] %s" % (strftime('%H:%M:%S', localtime()), out)
                print "[+] Cell Identity : "+cid
                print "[+] Mobile Country Code : "+mcc
                print "[+] Mobile Network Code : "+mnc
                print "[+] Location Area Code : "+lac

                if mcc+mnc in operateur:
                    op = operateur[mcc+mnc]
                    print "Opérateur : "+operateur[mcc+mnc]
                    if 'sfr' in operateur[mcc+mnc].lower():
                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/sfr.png" % BTSMAPPER_PATH, 24,24)
                    elif 'orange' in operateur[mcc+mnc].lower():
                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/orange.png" % BTSMAPPER_PATH, 24,24)
                    else:
                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)
                else:
                    op = '?'
                    print "Opérateur inconnu"
                    pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)

                    cid, lac, mnc = [int(cid,16),int(lac,16),int(mnc)]
                    a = "000E00000000000000000000000000001B0000000000000000000000030000"
                    b = hex(cid)[2:].zfill(8) + hex(lac)[2:].zfill(8)
                    c = hex(divmod(mnc,100)[1])[2:].zfill(8) + hex(divmod(mnc,100)[0])[2:].zfill(8)
                    string = (a + b + c + "FFFFFFFF00000000").decode("hex")

                    r = urllib.urlopen("http://www.google.com/glm/mmap",string).read().encode("hex")
                    if len(r) > 14:
                        lon, lat = float(int(r[14:22], 16)) / 1000000, float(int(r[22:30], 16)) / 1000000

                    print "Coordonnées : %f:%f" % (lon, lat)

                    [strftime("%H:%M:%S", localtime()), op, str(lon), str(lat), cid, mcc, mnc, lac]

            elif "Inform : [06 1c" in out: # SYSTEM INFORMATION TYPE 4
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            # else:
            #     print out
    except KeyboardInterrupt:
        os.system("kill -9 %d" % gammuProcess.pid)