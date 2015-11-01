#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import gtk.gdk
import subprocess
from time import sleep, strftime, localtime, mktime
from commands import getoutput
#import urllib
from struct import pack, unpack
from httplib import HTTP

from btsmapper.core.db import BTS
from btsmapper.core.constants import BTSMAPPER_PATH


def msgbox(message, type_msg=0):
    about = gtk.MessageDialog(None,
                              gtk.DIALOG_MODAL,
                              gtk.MESSAGE_WARNING if type_msg else gtk.MESSAGE_INFO,
                              gtk.BUTTONS_OK,
                              message)
    about.run()
    about.destroy()

os.system("clear")
try:
    if not 'gammu:' in getoutput("killall gammu"):
        print "[!] Killing previous gammu process"

    print "[+] Checking connectivity (skip with 'kill gammu' button)"

    resIdentify = getoutput("gammu --config %s/core/gammurc --identify" % BTSMAPPER_PATH)

    #TODO This check is for a french configuration, change this check or add other languages...
    if "n'existe pas" in resIdentify:
        gtk.gdk.threads_enter()
        msgbox("Connectivity problem !\nCheck you're Nokia 3310 device", 1)
        gtk.gdk.threads_leave()
    else:
        gammuProcess = subprocess.Popen(("gammu", "--config", "%s/core/gammurc" % BTSMAPPER_PATH, "--nokiadebug", "%s/core/nhm5_587.txt" % BTSMAPPER_PATH, "v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print "[+] Subprocess launched (pid=%s)" % gammuProcess.pid

        operateur = {   # Grèce
                        "20201": "COSMOTE",
                        "20205": "GR PANAFON",
                        "20210": "GR HSTET",
                        # Pays-Bas
                        "20404": "NL LIBERTEL",
                        "20408": "NL KPN",
                        "20412": "NL TELFORT",
                        "20416": "Ben NL",
                        "20420": "NL DUTCHTONE",
                        # Belgique
                        "20601": "BEL PROXIMUS",
                        "20610": "B mobistar",
                        "20620": "BASE",
                        # France
                        "20801": "Orange",
                        "20802": "Orange",
                        "20805": "Globalstar Europe",
                        "20806": "Globalstar Europe",
                        "20807": "Globalstar Europe",
                        "20809": "SFR",
                        "20810": "SFR",
                        "20811": "SFR",
                        "20813": "SFR",
                        "20814": "RFF",
                        "20815": "Free Mobile",
                        "20820": "Bouygues Télécom",
                        "20821": "Bouygues Télécom",
                        # Andorre
                        "21303": "AND M-AND",
                        # Espagne
                        "21401": "E AIRTEL",
                        "21402": "MOVISTAR",
                        "21403": "E AMENA",
                        "21407": "MOVISTAR",
                        # Suisse
                        "22801": "Swisscom",
                        "22802": "Sunrise Suisse",
                        "22803": "Orange CH",
                        # Autres
                        "34001": "Orange Caraibe",
                        "64700": "Orange Réunion"}

        while True:
            out = gammuProcess.stdout.readline().rstrip('\n')
            # print out

            if not out and gammuProcess.poll() is not None:
                break

            if "Warning" in out or "Error" in out:
                print "[!] " + out
                #TODO This check is for a french configuration, change this check or add other languages...
                if "verrouillé" in out:
                    print "[!] Killing gammu process"
                    os.system("killall gammu")
                    gammuProcess=subprocess.Popen(("gammu", "--config", "%s/core/gammurc" % BTSMAPPER_PATH, "--nokiadebug", "%s/core/nhm5_587.txt" % BTSMAPPER_PATH, "v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print "[+] Subprocess relaunched"
                    print "[+] Please wait 3 seconds"
                    sleep(3)

            # SYSTEM INFORMATION TYPE 1
            elif "Inform : [06 19" in out:
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            # SYSTEM INFORMATION TYPE 2
            elif "Inform : [06 1a" in out:
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            # SYSTEM INFORMATION TYPE 3
            elif "Inform : [06 1b" in out:
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out, '\n'

                out = re.search("Inform : \[([\d\w ]*)\]", out, re.MULTILINE).groups()[0]
                cid = "".join(out.split()[2:4])
                mcc = "".join(x[::-1].replace("f", "") for x in out.split()[4:6])
                mnc = out.split()[6]
                lac = "".join(out.split()[7:9])
                date = int(mktime(localtime()))
                out = "\033[1;33;40m%s \033[1;34;40m%s \033[1;33;40m%s \033[1;34;40m%s \033[1;33;40m%s \033[0;0m%s" % (
                    ' '.join(out.split()[0:2]),
                    ' '.join(out.split()[2:4]),
                    ' '.join(out.split()[4:6]),
                    out.split()[6],
                    ' '.join(out.split()[7:9]),
                    ' '.join(out.split()[9:])
                )

                print "[%s] %s" % (strftime('%H:%M:%S', localtime()), out)
                print "[+] Cell Identity : " + cid
                print "[+] Mobile Country Code : " + mcc
                print "[+] Mobile Network Code : " + mnc
                print "[+] Location Area Code : " + lac

                if mcc+mnc in operateur:
                    op = operateur[mcc+mnc]
                    print "[+] Telecoms company : %s" % operateur[mcc+mnc]
                else:
                    op = '?'
                    print "[!] Telecoms company code unknown"


                # Don't work anymore (on 23/10/2015)
                #a = "000E00000000000000000000000000001B0000000000000000000000030000"
                #b = hex(cid)[2:].zfill(8) + hex(lac)[2:].zfill(8)
                #c = hex(divmod(mnc,100)[1])[2:].zfill(8) + hex(divmod(mnc,100)[0])[2:].zfill(8)
                #string = (a + b + c + "FFFFFFFF00000000").decode("hex")
                #r = urllib.urlopen("http://www.google.com/glm/mmap",string).read().encode("hex")
                #if len(r) > 14:
                #    lon, lat = float(int(r[14:22], 16)) / 1000000, float(int(r[22:30], 16)) / 1000000

                cid, lac, mnc = [int(cid, 16), int(lac, 16), int(mnc)]
                country = 'fr'
                device = 'Nokia N95 8Gb'
                b_string = pack('>hqh2sh13sh5sh3sBiiihiiiiii',
                                21, 0,
                                len(country), country,
                                len(device), device,
                                len('1.3.1'), "1.3.1",
                                len('Web'), "Web",
                                27, 0, 0,
                                3, 0, cid, lac,
                                0, 0, 0, 0)
                http = HTTP('www.google.com', 80)
                http.putrequest('POST', '/glm/mmap')
                http.putheader('Content-Type', 'application/binary')
                http.putheader('Content-Length', str(len(b_string)))
                http.endheaders()
                http.send(b_string)
                code, msg, headers = http.getreply()
                bytes = http.file.read()
                (a, b, errorCode, latitude, longitude, c, d, e) = unpack(">hBiiiiih", bytes)
                lat = latitude / 1000000.0
                lon = longitude / 1000000.0

                print "[+] Coordinates : %f:%f" % (lat, lon)

                if not BTS.if_already_mapped(lat, lon):
                    try:
                        bts = BTS.create(
                            op=op,
                            lat=lat,
                            lon=lon,
                            cid=cid,
                            mcc=mcc,
                            mnc=mnc,
                            lac=lac,
                            date=date
                        )
                    except Exception as err:
                        print "Error : %s" % err
                else:
                    print "[!] Already in database"

            # SYSTEM INFORMATION TYPE 4
            elif "Inform : [06 1c" in out:
                print '\n', gammuProcess.stdout.readline().rstrip().lstrip()
                print gammuProcess.stdout.readline().rstrip().lstrip()
                print out

            # else:
            #     print out

except (KeyboardInterrupt, SystemExit):
    try:
        os.system("kill -9 %d" % gammuProcess.pid)
    except:
        print "[+] Exit"
    finally:
        print "[+] Exit (pid=%s)" % gammuProcess.pid
