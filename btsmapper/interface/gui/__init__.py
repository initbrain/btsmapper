#!/usr/bin/env python
# -*- coding:utf-8 -*-

import_error = ''

import re
import sys
import os.path
import gtk.gdk
import gobject
from time import sleep

try:
    from commands import getoutput, getstatusoutput
except ImportError:
    import_error += "\ncommands"

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
    def quitDialog(self, widget, data):
        if self.yesnoDialog("Voulez-vous vraiment quitter\nFree-knowledge Python BTS Mapper ?"):
            delete()
        else:
            return 1

    def yesnoDialog(self, message):
        # Creation de la boite de message
        # Type : Question -> gtk.MESSAGE_QUESTION
        # Boutons : 1 OUI, 1 NON -> gtk.BUTTONS_YES_NO
        question = gtk.MessageDialog(self,
                                     gtk.DIALOG_MODAL,
                                     gtk.MESSAGE_QUESTION,
                                     gtk.BUTTONS_YES_NO,
                                     message)

        # Affichage et attente d une reponse
        reponse = question.run()
        question.destroy()
        if reponse == gtk.RESPONSE_YES:
            return 1
        elif reponse == gtk.RESPONSE_NO:
            return 0

    def locHistory(self, parent):
        try:
            lon = self.liststore_geoloc.get_value(self.treeview_sortie_geoloc.get_selection().get_selected()[1],2)
            lat = self.liststore_geoloc.get_value(self.treeview_sortie_geoloc.get_selection().get_selected()[1],3)
        except TypeError as err:
            print "Erreur : %s" % err
        else:
            self.osm.set_center_and_zoom(float(lon), float(lat), 16)

    def __init__(self):
        self.fenetre = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.fenetre.set_resizable(True)            # Autoriser le redimensionnement de la fenêtre
        self.fenetre.set_title("Free-knowledge Python BTS Mapper")    # Titre de la fenêtre
        #self.fenetre.set_decorated(False)            # Cacher les contours de la fenêtre
        self.fenetre.set_icon_from_file("%s/images/icone.png" % BTSMAPPER_PATH)    # Spécifie une icône
        self.fenetre.set_position(gtk.WIN_POS_CENTER)        # Centrer la fenêtre au lancement
        self.fenetre.set_border_width(10)            # Largueur de la bordure intérieur
        self.fenetre.set_size_request(1000, 500)            # Taille de la fenêtre
        self.fenetre.connect("delete_event", self.quitDialog)    # Alerte de fermeture
        self.fenetre.connect('key-press-event', lambda o, event: event.keyval == gtk.keysyms.F11 and self.toggle_fullscreen())
        self.fenetre.show()

        self.vbox = gtk.VBox(False, 0)
        self.fenetre.add(self.vbox)

        self.hbox = gtk.HBox(True, 0)
        self.vbox.pack_start(self.hbox)

        import vte
        self.vterm = vte.Terminal()
        self.vterm.set_scrollback_lines(-1)
        self.vterm.allow_bold = True
        self.vterm.audible_bell = True
        self.foreground = gtk.gdk.color_parse('#FFFFFF')
        self.background = gtk.gdk.color_parse('#000000')
        self.vterm.set_color_foreground(self.foreground)
        self.vterm.set_color_background(self.background)
        # self.vterm.background_image_file = "%s/images/logo.png" % BTSMAPPER_PATH
        # self.vterm.connect("child-exited", lambda term: gtk.main_quit())

        self.hbox.pack_start(self.vterm)

        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            self.osm = osmgpsmap.GpsMap()
        self.osm.layer_add(
            osmgpsmap.GpsMapOsd(
                show_dpad=True,
                show_zoom=True)
        )
        self.osm.layer_add(
            DummyLayer()
        )

        self.osm.connect('button_release_event', self.map_clicked)

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        self.hbox.pack_start(self.osm)

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
        self.liststore_geoloc = gtk.ListStore(str, str, str, str, str, str, str, str)
        # scrollbar_sortie_geoloc
        scrolled_sortie_geoloc = gtk.ScrolledWindow()
        hbox.pack_start(scrolled_sortie_geoloc, True, True, 0)
        scrolled_sortie_geoloc.show()
        # self.treeasview_sortie_geoloc
        self.treeview_sortie_geoloc = gtk.TreeView(self.liststore_geoloc)
        self.treeview_sortie_geoloc.set_rules_hint(True)
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Heure", gtk.CellRendererText(), text=0))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Opérateur", gtk.CellRendererText(), text=1))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Longitude", gtk.CellRendererText(), text=2))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Latitude", gtk.CellRendererText(), text=3))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Cell Identity", gtk.CellRendererText(), text=4))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Mobile Country Code", gtk.CellRendererText(), text=5))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Mobile Network Code", gtk.CellRendererText(), text=6))
        self.treeview_sortie_geoloc.append_column(gtk.TreeViewColumn("Location Area Code", gtk.CellRendererText(), text=7))
        self.treeview_sortie_geoloc.set_headers_visible(True)
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
        self.btn2_geoloc = gtk.Button("Resize term")
        self.btn2_geoloc.set_size_request(int(self.btn2_geoloc.size_request()[0]*1.2),self.btn2_geoloc.size_request()[1])
        self.statuGeolocLoop = False
        # self.btn2_geoloc.connect('clicked', lambda e: thread.start_new_thread(self.geolocLoop, ()))
        self.btn2_geoloc.connect('clicked', lambda e: self.fenetre.set_size_request(1000, 500))#.set_size(80, 24))
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

        if os.geteuid() != 0:
            # Vérification des permissions
            for su_gui_cmd in ['gksu','kdesu','ktsuss','beesu','']:
                if getoutput("which "+su_gui_cmd):
                    break
            if not su_gui_cmd:
                about = gtk.MessageDialog(None,
                                          gtk.DIALOG_MODAL,
                                          gtk.MESSAGE_WARNING,
                                          gtk.BUTTONS_OK,
                                          "Un des outils suivant est nécessaire pour acquérir les droits administrateur, veuillez en installer un :\n" +\
                                          "\n" + \
                                          "gksu\n" + \
                                          "kdesu\n" + \
                                          "ktsuss\n" + \
                                          "beesu")
                gtk.gdk.threads_enter()
                about.run() # Affichage de la boite de message
                about.destroy() # Destruction de la boite de message
                gtk.gdk.threads_leave()
            else:
                self.vterm.fork_command()
                self.vterm.set_color_foreground(self.foreground)
                self.vterm.set_color_background(self.background)
                self.vterm.feed_child("%s '%s %s/interface/cli/__init__.py'\n" % (su_gui_cmd, sys.executable, BTSMAPPER_PATH))
        else:
            self.vterm.fork_command()
            self.vterm.set_color_foreground(self.foreground)
            self.vterm.set_color_background(self.background)
            self.vterm.feed_child("%s %s/interface/cli/__init__.py\n" % (sys.executable, BTSMAPPER_PATH))

            # while True:
            #     stdoutVterm = self.vterm.get_text()
            #     if not stdoutVterm:
            #         sleep(1)

            # print "\n"+strftime('%H:%M:%S', localtime())
            # out=re.search("Inform : \[([\d\w ]*)\]", out, re.MULTILINE).groups()[0]
            # print out
            #
            # cid="".join(out.split()[2:4])
            # print "Cell Identity : "+cid
            #
            # mcc="".join(x[::-1].replace("f","") for x in out.split()[4:6])
            # print "Mobile Country Code : "+mcc
            #
            # mnc=out.split()[6]
            # print "Mobile Network Code : "+mnc
            #
            # lac="".join(out.split()[7:9])
            # print "Location Area Code : "+lac
            #
            # if mcc+mnc in operateur:
            #     op = operateur[mcc+mnc]
            #     print "Opérateur : "+operateur[mcc+mnc]
            #     if 'sfr' in operateur[mcc+mnc].lower():
            #         pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/sfr.png" % BTSMAPPER_PATH, 24,24)
            #     elif 'orange' in operateur[mcc+mnc].lower():
            #         pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/orange.png" % BTSMAPPER_PATH, 24,24)
            #     else:
            #         pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)
            # else:
            #     op = '?'
            #     print "Opérateur inconnu"
            #     pb = gtk.gdk.pixbuf_new_from_file_at_size("%s/images/bts.png" % BTSMAPPER_PATH, 24,24)
            #
            # cid,lac,mnc=[int(cid,16),int(lac,16),int(mnc)]
            # a = "000E00000000000000000000000000001B0000000000000000000000030000"
            # b = hex(cid)[2:].zfill(8) + hex(lac)[2:].zfill(8)
            # c = hex(divmod(mnc,100)[1])[2:].zfill(8) + hex(divmod(mnc,100)[0])[2:].zfill(8)
            # string = (a + b + c + "FFFFFFFF00000000").decode("hex")
            #
            # r=urllib.urlopen("http://www.google.com/glm/mmap",string).read().encode("hex")
            # if len(r) > 14: lon,lat=float(int(r[14:22],16))/1000000,float(int(r[22:30],16))/1000000
            #
            # print "Coordonnées : %f:%f" % (lon, lat)
            #
            # try:
            #     self.osm.image_add(lon, lat, pb)
            #     # self.osm.set_center_and_zoom(lon, lat, 16)
            # except Exception as err:
            #     print "Erreur : %s" % err
            # else:
            #     self.liststore_geoloc.append([strftime("%H:%M:%S", localtime()), op, str(lon), str(lat), cid, mcc, mnc, lac])
            #     # if not self.statuGeolocLoop:
            #     #     self.btn_geoloc.set_label("Lancer une seule fois")
            #     #     self.btn_geoloc.set_sensitive(True)
            #     # else:
            #     #     self.btn_geoloc.set_label("Analyse en cours...")
            #     # self.osm.image_add(lon,lat,pb)
            #     #			self.osm.set_center_and_zoom(lon, lat, 12)

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

def delete():
    """Gestion des evenements de fermeture"""
    exit() # but gtk.main_quit() fail with KeyboardInterrupt ...

def main():
    # Exécution
    try:
        u = UI()
        u.fenetre.show_all()
        if os.name == "nt":
            gtk.gdk.threads_enter()
        gtk.main()
        if os.name == "nt":
            gtk.gdk.threads_leave()
    except (KeyboardInterrupt, SystemExit):
        delete()