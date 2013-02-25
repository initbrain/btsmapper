#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gestion des importations
import_error = "" # Variable de stockage des erreurs d'importation

# Modules utilisés pour l'interface graphique
try:
    import pygtk
except ImportError:
    import_error += "\npygtk 2.3.90 ou ultérieur"
try:
    import gtk
except ImportError:
    import_error += "\ngtk"
else:
    if gtk.pygtk_version < (2, 3, 90) and import_error == "":
        import_error += "\npygtk 2.3.90 ou ultérieur"
try:
    import inspect
except ImportError:
    import_error += "\ninspect"
try:
    import simplejson
except ImportError:
    import_error += "\nsimplejson"
try:
    import subprocess
except ImportError:
    import_error += "\nsubprocess"
try:
    from commands import getoutput, getstatusoutput
except ImportError:
    import_error += "\ncommands"

# Gestion des éventuelles erreurs d'importation

if import_error != "":
    print "Il est nécessaire de posséder les librairies suivantes pour faire fonctionner cette boîte à outils :" + import_error
    raise SystemExit

import os

from btsmapper import VERSION
from btsmapper.core.constants import BTSMAPPER_PATH, CONFIG_PATH


class install():
    def quitDialog(self, widget, data):
        if self.yesnoDialog("Voulez-vous vraiment quitter\nl'assistant d'installation ?"):
            exit()
        else:
            return 1

    def yesnoDialog(self, message):
        # Creation de la boite de message
        # Type : Question -> gtk.MESSAGE_QUESTION
        # Boutons : 1 OUI, 1 NON -> gtk.BUTTONS_YES_NO
        question = gtk.MessageDialog(self.fenetre,
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

    def msgbox(self, message, type_msg=0):
        about = gtk.MessageDialog(self.fenetre,
                                  gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_WARNING if type_msg else gtk.MESSAGE_INFO,
                                  gtk.BUTTONS_OK,
                                  message)
        about.run() # Affichage de la boite de message
        about.destroy() # Destruction de la boite de message

    def checkRoot(self):
        # Vérification des permissions
        for su_gui_cmd in ['gksu','kdesu','ktsuss','beesu','']:
            if getoutput("which "+su_gui_cmd): break
        if not su_gui_cmd:
            gtk.gdk.threads_enter()
            self.msgbox("Un des outils suivant est nécessaire pour acquérir les droits administrateur, veuillez en installer un :\n\ngksu\nkdesu\nktsuss\nbeesu",1)
            gtk.gdk.threads_leave()
        else:
            getstatusoutput(su_gui_cmd+" 'killall airodump-ng'")

    def checkLib(self, lib, type):
        if type == 'cmd':
            try:
                checkRes = getoutput("which " + lib)
            except ImportError:
                return False
            else:
                if checkRes and not "no %s" % lib in checkRes:
                    return True
                else:
                    return False
        elif type == 'lib':
            try:
                inspect.getfile(__import__(lib))
            except ImportError:
                return False
            else:
                return True

    def libInfos(self, widget, dependency, data):
        print "\nLibrairie : %s" % dependency['name']
        if dependency.has_key('homepage'):
            for homepage in dependency['homepage']:
                print "Site web : %s" % (homepage if homepage else "non précisé")
        else:
            print "Site web : non précisé"

        if dependency.has_key('doc'):
            for doc in dependency['doc']:
                print "Documentation : %s" % (doc if doc else "non précisée")
        else:
            print "Documentation : non précisée"

        if dependency.has_key('install'):
            for install in dependency['install']:
                if install['type'] and install['target']:
                    print "Type d'installation : %s" % install['type']
                    print "Cible : %s" % install['target']

                    if install.has_key('tested'):
                        for test in install['tested']:
                            print "Testée avec : %s" % test if test else "Non testée"
                    else:
                        print "Non testée ..."

                    if install['type'] and len(install['type'][0]) != 1:
                        installType = install['type']
                    else:
                        installType = [install['type']]

                    if self.checkLib(dependency['name'], dependency['type']):
                        for key in self.btns.keys():
                            if dependency['name'] in key:
                                self.btns[key].child.set_text('<i><span foreground="green">%s</span></i>' % dependency['name'])
                                self.btns[key].child.set_use_markup(True)
                        print '--> déjà installé'
                        return True


                    packageInstallers = ['apt-get install',
                                         'yum install',
                                         'emerge',
                                         'urpmi',
                                         'zypper install',
                                         '']

                    for packageInstaller in [y.split(' ')[0] for y in packageInstallers]:
                        checkRes = getoutput("which " + packageInstaller)
                        if checkRes and not "no %s" % packageInstaller in checkRes:
                            break
                    if packageInstaller:
                        print "--> votre gestionnaire de paquet est : %s" % packageInstaller
                    else:
                        print "--> impossible de déterminer votre gestionnaire de paquet"

                    i = 0
                    for x in installType:
                        if i and self.checkLib(dependency['name'], dependency['type']):
                            for key in self.btns.keys():
                                if dependency['name'] in key:
                                    self.btns[key].child.set_text('<i><span foreground="green">%s</span></i>' % dependency['name'])
                                    self.btns[key].child.set_use_markup(True)
                            print '--> déjà installé'
                            return True

                        target = install['target'][i] if len(installType) > 1 else install['target']

                        if target and len(target[0]) == 1:
                            target = [target]

                        print ' '.join([x] + target)

                        if x == 'easy_install':
                            self.eiProcess = subprocess.Popen(['easy_install'] + target, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            while True:
                                err = self.eiProcess.stderr.readline().rstrip('\n')
                                if err:
                                    print '@', err #TODO couleur rouge ?
                                out = self.eiProcess.stdout.readline().rstrip('\n')
                                if out:
                                    print '#', out #TODO couleur normale
                                    if "No local packages or download links found" in out:
                                        print "=> Paquet introuvable via easy_install" #TODO erreur
                                elif self.eiProcess.poll() != None:
                                    print '--> fin'
                                    break

                        if x == 'pip':
                            self.pipProcess = subprocess.Popen(['pip', 'install'] + target, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            while True:
                                err = self.pipProcess.stderr.readline().rstrip('\n')
                                if err:
                                    print '@', err #TODO couleur rouge ?
                                out = self.pipProcess.stdout.readline().rstrip('\n')
                                if out:
                                    print '#', out #TODO couleur normale
                                    if "No distributions at all found" in out:
                                        print "=> Paquet introuvable via pip" #TODO erreur
                                elif self.pipProcess.poll() != None:
                                    print '--> fin'
                                    break

                        if x == 'apt-get' and x == packageInstaller:
                            self.agProcess = subprocess.Popen(['apt-get', 'install', '-y'] + target, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            while True:
                                err = self.agProcess.stderr.readline().rstrip('\n')
                                if err:
                                    print '@', err #TODO couleur rouge ?
                                    if "Impossible de trouver le paquet" in err:
                                        print "=> Paquet introuvable via apt-get" #TODO erreur
                                out = self.agProcess.stdout.readline().rstrip('\n')
                                if out:
                                    print '#', out #TODO couleur normale
                                elif self.agProcess.poll() != None:
                                    print '--> fin'
                                    break

                        if x == 'yum' and x == packageInstaller:
                            self.agProcess = subprocess.Popen(['yum', 'install'] + target + ['-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            while True:
                                err = self.agProcess.stderr.readline().rstrip('\n')
                                if err:
                                    print '@', err #TODO couleur rouge ?
                                    if "Aucun paquet" in err:
                                        print "=> Paquet introuvable via yum" #TODO erreur
                                out = self.agProcess.stdout.readline().rstrip('\n')
                                if out:
                                    print '#', out #TODO couleur normale
                                elif self.agProcess.poll() != None:
                                    print '--> fin'
                                    break
                        i += 1
                else:
                    print "Type d'installation : non précisée"
                    return False
        else:
            print "Type d'installation : non précisée"
            return False

    def __init__(self):
        self.fenetre = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.fenetre.set_resizable(False) # Interdire le redimensionnement de la fenêtre
        self.fenetre.set_title("Installation Free-knowledge Python BTS Mapper") # Titre de la fenêtre
        #self.fenetre.set_decorated(False) # Cacher les contours de la fenêtre
        self.fenetre.set_icon_from_file("%s/images/icone.png" % BTSMAPPER_PATH) # Spécifier une icône
        self.fenetre.set_position(gtk.WIN_POS_CENTER) # Centrer la fenêtre au lancement
        self.fenetre.set_border_width(0) # Largueur de la bordure intérieur
        # self.fenetre.set_size_request(430, 400) # Taille de la fenêtre
        self.fenetre.connect("delete_event", self.quitDialog)    # Alerte de fermeture
        self.fenetre.show()

        self.boite_all = gtk.VBox(False, 5)
        self.boite_all.show()

        self.fixed_img = gtk.Fixed()
        self.fixed_img.set_size_request(430,150)
        self.fixed_img.show()

        self.img_a_propos = gtk.Image()
        self.img_a_propos.set_from_file("%s/images/a_propos.png" % BTSMAPPER_PATH)
        self.img_a_propos.show()
        self.fixed_img.put(self.img_a_propos, 0, 0)

        self.version = gtk.Label("v%s" % VERSION)
        self.version.show()
        self.fixed_img.put(self.version, 20, 80)

        self.boite_all.pack_start(self.fixed_img, False, False, 0)

        # self.boite_modules
        self.boite_modules = gtk.VBox(False, 5)
        self.boite_modules.set_border_width(10)
        self.boite_modules.show()

        # label1_modules
        label1_modules = gtk.Label("Installer les dépendances :")
        label1_modules.set_alignment(0, 0)
        self.boite_modules.pack_start(label1_modules, True, True, 0)
        label1_modules.show()

        # scrollbar_entree
        self.scrolled_modules = gtk.ScrolledWindow()
        self.scrolled_modules.set_size_request(250, 200)
        self.boite_modules.pack_start(self.scrolled_modules, False, False, 0)
        self.scrolled_modules.show()

        self.boite_site_modules = gtk.HBox(False, 0)
        self.scrolled_modules.add_with_viewport(self.boite_site_modules)
        self.scrolled_modules.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.boite_site_modules.show()

        self.boite_col1_modules = gtk.VBox(False, 0)
        self.boite_site_modules.pack_start(self.boite_col1_modules, True, True, 0)
        self.boite_col1_modules.show()

        json_data=open('%s/core/modules.json' % BTSMAPPER_PATH)
        data = simplejson.load(json_data)
        json_data.close()

        # for cathegorie in data.keys():
        #     print "cathegorie : %s" % cathegorie
        #     for module in data[cathegorie]:
        #         print "module : %s" % module['name']
        #         for dependance in module['dependency']:
        #             if dependance['name']:
        #                 print "dependance : %s" % dependance['name']

        i = 0
        self.expanders = dict()
        self.vboxs = dict()
        self.hboxs = dict()
        self.checkbtns = dict()
        self.btns = dict()
        self.labels = dict()
        for category in data.keys():
            self.expanders[category] = gtk.Expander("<b>%s</b>" % category)
            self.expanders[category].props.use_markup = True
            self.expanders[category].set_expanded(True)
            self.boite_col1_modules.pack_start(self.expanders[category], False, False, 0)
            self.expanders[category].show()

            self.vboxs[category] = gtk.VBox(False, 0)
            self.expanders[category].add(self.vboxs[category])
            self.vboxs[category].show()

            for module in data[category]:
                i+=1
                self.checkbtns[module['name']] = gtk.CheckButton(module['name'])
                self.vboxs[category].pack_start(self.checkbtns[module['name']], False, False, 0)
                self.checkbtns[module['name']].set_active(True)
                self.checkbtns[module['name']].show()

                for dependency in module['dependency']:
                    if dependency['name']:
                        self.hboxs['%s - %s' % (dependency['name'], module['name'])] = gtk.HBox()
                        self.vboxs[category].pack_start(self.hboxs['%s - %s' % (dependency['name'], module['name'])], fill=False)
                        self.hboxs['%s - %s' % (dependency['name'], module['name'])].show()

                        if self.checkLib(dependency['name'], dependency['type']):
                            self.btns['%s - %s' % (dependency['name'], module['name'])] = gtk.Button('<i><span foreground="green">%s</span></i>' % dependency['name'])
                        else:
                            self.btns['%s - %s' % (dependency['name'], module['name'])] = gtk.Button('<i><span foreground="red">%s</span></i>' % dependency['name'])

                        self.btns['%s - %s' % (dependency['name'], module['name'])].child.set_use_markup(True)
                        self.btns['%s - %s' % (dependency['name'], module['name'])].set_size_request(int(self.btns['%s - %s' % (dependency['name'], module['name'])].size_request()[0]*1.2),self.btns['%s - %s' % (dependency['name'], module['name'])].size_request()[1])
                        self.btns['%s - %s' % (dependency['name'], module['name'])].connect("clicked", self.libInfos, dependency, data)

                        self.hboxs['%s - %s' % (dependency['name'], module['name'])].pack_start(self.btns['%s - %s' % (dependency['name'], module['name'])], False, False, 0)
                        self.btns['%s - %s' % (dependency['name'], module['name'])].show()

        self.boite2_modules = gtk.HBox(False, 5)
        self.boite_modules.pack_start(self.boite2_modules, False, False, 5)
        self.boite2_modules.show()

        # self.progressbar_modules
        self.progressbar_modules = gtk.ProgressBar()
        self.boite2_modules.pack_start(self.progressbar_modules, True, True, 0)
        self.progressbar_modules.show()

        # self.self.btn_modules
        self.btn_modules = gtk.Button("ok")
        self.btn_modules.set_size_request(int(self.btn_modules.size_request()[0]*1.2),self.btn_modules.size_request()[1])
        self.btn_modules.connect("clicked", lambda e: exit())
        self.boite2_modules.pack_start(self.btn_modules, False, False, 0)
        self.btn_modules.show()

        # self.separateur_modules
        self.separateur_modules = gtk.HSeparator()
        self.boite_modules.pack_start(self.separateur_modules, False, False, 0)
        self.separateur_modules.show()

        # self.label_entree_modules
        self.label_entree_modules = gtk.Label("GNU General Public License v3.0")
        self.label_entree_modules.set_alignment(1,0)
        self.boite_modules.pack_start(self.label_entree_modules, False, False, 0)
        self.label_entree_modules.show()

        self.boite_all.pack_start(self.boite_modules, False, False, 0)

        self.fenetre.add(self.boite_all)
        # self.fenetre.show_all()
        gtk.main()

def main():
    """
    test

    """
    print "\nLancement de l'assistant d'installation ..."
    install()

if __name__ == "__main__":
    main()
