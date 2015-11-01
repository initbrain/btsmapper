# -*- coding: utf-8 -*-

from time import mktime, localtime, sleep
from peewee import SqliteDatabase, Model, RawQuery
from peewee import CharField, IntegerField, FloatField, BooleanField

from btsmapper.core.constants import BTSMAPPER_PATH


class BTSdb(SqliteDatabase):
    """
    SQLite database object.
    """
    def connect(self):
        super(BTSdb, self).connect()
        pragma = RawQuery(BaseModel, "PRAGMA foreign_keys = ON;")
        self.execute(pragma)


class BaseModel(Model):
    """
    Basic database model, uses RSSdb as the database object.
    """
    class Meta:
        database = BTSdb("%s/core/results.db" % BTSMAPPER_PATH, check_same_thread=False)


class BTS(BaseModel):
    """
    BTS model.
    """
    op = CharField(max_length=256, null=True)
    lat = FloatField(null=True)
    lon = FloatField(null=True)
    cid = CharField(max_length=256, null=True)
    mcc = CharField(max_length=256, null=True)
    mnc = CharField(max_length=256, null=True)
    lac = CharField(max_length=256, null=True)
    date = IntegerField(default=int(mktime(localtime())))
    mapped = BooleanField(default=False)

    def __str__(self):
        return "<BTS '%s (%f:%f)'>" % (self.op, self.lat, self.lon)

    @classmethod
    def get_already_mapped(cls):
        try:
            query = cls.select().where(
                cls.mapped == True
            )
        except BTS.DoesNotExist as err:
            return False
        else:
            return query

    @classmethod
    def get_non_mapped(cls):
        while True:
            try:
                query = cls.select().where(
                    cls.mapped == False
                )
                query.get()
            except BTS.DoesNotExist as err:
                sleep(3)
            else:
                return query

    @classmethod
    def if_already_mapped(cls, lat, lon):
        while True:
            try:
                query = cls.select().where(
                    cls.lat == lat,
                    cls.lon == lon,
                    cls.mapped == True
                ).get()
            except BTS.DoesNotExist as err:
                return False
            else:
                return query


BTS.create_table(fail_silently=True)
