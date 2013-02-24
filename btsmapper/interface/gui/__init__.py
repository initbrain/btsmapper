#!/usr/bin/env python
# -*- coding:utf-8 -*-

import_error = ''

import re
import sys
import os.path
import gtk.gdk
import gobject

try: import thread
except ImportError: import_error+="\nthread"

from btsmapper.core.constants import BTSMAPPER_PATH

gobject.threads_init()
gtk.gdk.threads_init()

#Try static lib first
mydir = os.path.dirname(os.path.abspath(__file__))
libdir = os.path.abspath(os.path.join(mydir, "..", "python", ".libs"))
sys.path.insert(0, libdir)

import osmgpsmap
print "using library: %s (version %s)" % (osmgpsmap.__file__, osmgpsmap.__version__)

#assert osmgpsmap.__version__ == "0.7.3"

class DummyMapNoGpsPoint(osmgpsmap.GpsMap):
    def do_draw_gps_point(self, drawable):
        pass
gobject.type_register(DummyMapNoGpsPoint)

class DummyLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    def __init__(self):
        gobject.GObject.__init__(self)

    def do_draw(self, gpsmap, gdkdrawable):
        pass

    def do_render(self, gpsmap):
        pass

    def do_busy(self):
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        return False
gobject.type_register(DummyLayer)

class UI(gtk.Window):
    def locHistory(self, parent):
        try: choix = self.liststore_geoloc.get_value(self.treeview_sortie_geoloc.get_selection().get_selected()[1], 1)
        except TypeError as err:
            print "Erreur : %s" % err
        else:
            result = re.compile("longitude : ([\d\:\.-]+), latitude : ([\d\:\.-]+)", re.MULTILINE).findall(choix)
            #print result[0][0]+", "+result[0][1]
            self.osm.set_center_and_zoom(float(result[0][1]), float(result[0][0]), 16)

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_default_size(500, 500)
        self.connect('destroy', lambda x: gtk.main_quit())
        self.set_title('OpenStreetMap BTS Mapper')

        self.vbox = gtk.VBox(False, 0)
        self.add(self.vbox)

        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            self.osm = osmgpsmap.GpsMap()
        self.osm.layer_add(
            osmgpsmap.GpsMapOsd(
                show_dpad=True,
                show_zoom=True))
        self.osm.layer_add(
            DummyLayer())

        self.osm.connect('button_release_event', self.map_clicked)

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        self.vbox.pack_start(self.osm)

        gobject.timeout_add(500, self.print_tiles)
        self.osm.set_center_and_zoom(46.227638, 2.213749, 5) # Centrer sur la France

        ex = gtk.Expander("<b>Historique</b>")
        ex.props.use_markup = True

        vb = gtk.VBox()
        ex.add(vb)

        self.debug_button = gtk.Button("Commencer la géolocalisation")
        self.debug_button.connect('clicked', lambda e: thread.start_new_thread(self.debug_clicked, ()))

        hbox = gtk.HBox(True, 0)

        # self.liststore_geoloc
        self.liststore_geoloc = gtk.ListStore(str, str)
        # scrollbar_sortie_geoloc
        scrolled_sortie_geoloc = gtk.ScrolledWindow()
        hbox.pack_start(scrolled_sortie_geoloc, True, True, 0)
        scrolled_sortie_geoloc.show()
        # self.treeasview_sortie_geoloc
        self.treeview_sortie_geoloc = gtk.TreeView(self.liststore_geoloc)
        self.treeview_sortie_geoloc.set_rules_hint(True)
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Heure", gtk.CellRendererText(), text=0))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Position", gtk.CellRendererText(), text=1))
        self.treeview_sortie_geoloc.set_headers_visible(False)
        self.treeview_sortie_geoloc.connect("cursor-changed", self.locHistory)
        scrolled_sortie_geoloc.add(self.treeview_sortie_geoloc)
        scrolled_sortie_geoloc.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.treeview_sortie_geoloc.show()

        vb.pack_start(hbox, True)

        self.vbox.pack_start(ex, False, True, 0)

        hbox.show()
        vb.show()
        ex.show()

        # boite2_geoloc
        boite2_geoloc = gtk.HBox(False, 5)
        self.vbox.pack_start(boite2_geoloc, False, False, 0)
        boite2_geoloc.show()

        # self.btn_geoloc
        self.btn_geoloc = gtk.Button("Lancer l'analyse")
        self.btn_geoloc.set_size_request(int(self.btn_geoloc.size_request()[0]*1.2),self.btn_geoloc.size_request()[1])
        # self.btn_geoloc.connect('clicked', lambda e: thread.start_new_thread(self.geoloc, ()))
        self.btn_geoloc.connect('clicked', lambda e: thread.start_new_thread(self.debug_clicked, ()))

        boite2_geoloc.pack_start(self.btn_geoloc, True, True, 0)
        self.btn_geoloc.show()

        # self.btn2_geoloc
        self.btn2_geoloc = gtk.Button("Lancer")
        self.btn2_geoloc.set_size_request(int(self.btn2_geoloc.size_request()[0]*1.2),self.btn2_geoloc.size_request()[1])
        self.statuGeolocLoop = False
        # self.btn2_geoloc.connect('clicked', lambda e: thread.start_new_thread(self.geolocLoop, ()))
        self.btn2_geoloc.connect('clicked', lambda e: thread.start_new_thread(self.debug_clicked, ()))
        boite2_geoloc.pack_start(self.btn2_geoloc, False, False, 0)
        self.btn2_geoloc.show()

    def print_tiles(self):
        if self.osm.props.tiles_queued != 0:
            print self.osm.props.tiles_queued, 'tiles queued'
        return True

    def zoom_in_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom + 1)

    def zoom_out_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom - 1)

    def debug_clicked(self):
    #	self.osm.set_center_and_zoom(50.27, 3.97, 12)

        import subprocess, re, urllib
        from os import system
        from time import strftime, localtime

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

        gammuProcess=subprocess.Popen(("gammu","--nokiadebug","%s/core/nhm5_587.txt" % BTSMAPPER_PATH,"v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print "[+] Subprocess launched"

        while 1:
            out=gammuProcess.stdout.readline().rstrip('\n')
            if not out and gammuProcess.poll() != None:
                print "[!] Subprocess stopped"
                about = gtk.MessageDialog(None,
                                          gtk.DIALOG_MODAL,
                                          gtk.MESSAGE_WARNING,
                                          gtk.BUTTONS_OK,
                                          "Attention, le nokia n'est pas/plus détecté !\n\nDébranché ?\nPlus de batterie ?")
                about.run() # Affichage de la boite de message
                about.destroy() # Destruction de la boite de message
                break
            elif "Warning" in out or "Erreur" in out:
                print "[!] "+out
                if "verrouillé" in out: # À vérifier avec un output anglais
                    system("sudo killall gammu")
                    print "[!] Killing gammu process"
                    gammuProcess=subprocess.Popen(("gammu","--nokiadebug","%s/core/nhm5_587.txt" % BTSMAPPER_PATH,"v20-25,v18-19"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print "[+] Subprocess relaunched"
            elif "Inform : [06 1b" in out: # SYSTEM INFORMATION TYPE 3
                print "\n"+strftime('%H:%M:%S', localtime())
                out=re.search("Inform : \[([\d\w ]*)\]", out, re.MULTILINE).groups()[0]
                print out

                cid="".join(out.split()[2:4])
                print "Cell Identity : "+cid

                mcc="".join(x[::-1].replace("f","") for x in out.split()[4:6])
                print "Mobile Country Code : "+mcc

                mnc=out.split()[6]
                print "Mobile Network Code : "+mnc

                lac="".join(out.split()[7:9])
                print "Location Area Code : "+lac

                if mcc+mnc in operateur:
                    print "Opérateur : "+operateur[mcc+mnc]
                    if 'sfr' in operateur[mcc+mnc].lower():

                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/sfr.png" % BTSMAPPER_PATH, 24,24)

                    elif 'orange' in operateur[mcc+mnc].lower():
                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/orange.png" % BTSMAPPER_PATH, 24,24)
                    else:
                        pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)
                else:
                    print "Opérateur inconnu"
                    pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)

                cid,lac,mnc=[int(cid,16),int(lac,16),int(mnc)]
                a = "000E00000000000000000000000000001B0000000000000000000000030000"
                b = hex(cid)[2:].zfill(8) + hex(lac)[2:].zfill(8)
                c = hex(divmod(mnc,100)[1])[2:].zfill(8) + hex(divmod(mnc,100)[0])[2:].zfill(8)
                string = (a + b + c + "FFFFFFFF00000000").decode("hex")

                r=urllib.urlopen("http://www.google.com/glm/mmap",string).read().encode("hex")
                if len(r) > 14: lon,lat=float(int(r[14:22],16))/1000000,float(int(r[22:30],16))/1000000

                print "Coordonnées : %f:%f" % (lon, lat)

                try:
                    self.osm.image_add(lon, lat, pb)
                    # self.osm.set_center_and_zoom(lon, lat, 16)
                except Exception as err:
                    print "Erreur : %s" % err
                else:
                    self.liststore_geoloc.append(["[" + strftime("%H:%M:%S", localtime()) + "]", "latitude : " + str(lat) + ", longitude : " + str(lon)])
                    if not self.statuGeolocLoop:
                        self.btn_geoloc.set_label("Lancer une seule fois")
                        self.btn_geoloc.set_sensitive(True)
                    else:
                        self.btn_geoloc.set_label("Analyse en cours...")
                # self.osm.image_add(lon,lat,pb)
            #			self.osm.set_center_and_zoom(lon, lat, 12)

    def cache_clicked(self, button):
        bbox = self.osm.get_bbox()
        self.osm.download_maps(
            *bbox,
            zoom_start=self.osm.props.zoom,
            zoom_end=self.osm.props.max_zoom
        )

    def map_clicked(self, osm, event):
        lat,lon = self.osm.get_event_location(event).get_degrees()
        if event.button == 3:
            pb = gtk.gdk.pixbuf_new_from_file_at_size ("%s/images/poi.png" % BTSMAPPER_PATH, 24,24)
            self.osm.image_add(lat,lon,pb)

def main():
    u = UI()
    u.show_all()
    if os.name == "nt": gtk.gdk.threads_enter()
    gtk.main()
    if os.name == "nt": gtk.gdk.threads_leave()

if __name__ == "__main__":
    u = UI()
    u.show_all()
    if os.name == "nt": gtk.gdk.threads_enter()
    gtk.main()
    if os.name == "nt": gtk.gdk.threads_leave()
