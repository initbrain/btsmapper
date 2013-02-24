# -*- coding: utf-8 -*-

import sys
from collections import defaultdict
from fktb.core.log import logging


class Result(object):
    """
    Objet utilisé pour stocker les données de résultats et d'erreurs en gérant automatiquement
    le contexte dans lequel il est utilisé (mode console ou librairie).
    """
    cli_mode = False

    def __init__(self):
        self.data = list()
        self.format = list()
        self.errors = defaultdict(list)
    def __len__(self):
        """len(obj)"""
        return len(self.data)
    def __iter__(self):
        """iter(obj)"""
        return iter(self.data)
    def __getitem__(self, item):
        """obj[item]"""
        return self.data.__getitem__(item)
    def __setitem__(self, key, value):
        """obj[key] = value"""
        self.data.__setitem__(key, value)
    def __getslice__(self, start, end):
        """obj[start:end]"""
        return self.data.__getslice__(start, end)

    @property
    def has_results(self):
        return len(self.data) > 0
    @property
    def results_count(self):
        return len(self.data)

    @property
    def has_errors(self):
        return len(self.errors) > 0
    @property
    def errors_count(self):
        return sum([len(v) for _, v in self.errors.iteritems()])

    def add_error(self, exc_obj, message=None, level=logging.ERROR, display=True):
        """
        Ajout d'une erreur.
        En mode console, affiche également l'erreur reçue.
        """
        if message is None:
            message = getattr(exc_obj, 'message', str(exc_obj))
        self.errors[exc_obj].append(message)
        if display:
            self.log(message, level)

    def add_data(self, data, fmt_string=None, display=True):
        """
        Ajout d'un resultat.
        En mode console, affiche également les données reçues.
        """
        self.data.append(data)
        if fmt_string:
            self.format.append(fmt_string)
        else:
            self.format.append(None)
        message = data if (fmt_string is None) else (fmt_string % data)
        if display:
            self.log(message)

    @classmethod
    def log(cls, message, level=logging.INFO):
        """
        Utilise le module logging pour afficher des informations.
        En mode librairie, cette methode est une no-op.
        """
        logger = logging.getLogger(
            name=sys._getframe(1).f_globals.get('__name__', __name__)
        )
        if cls.cli_mode:
            logger.log(level, message)
