# -*- coding: utf-8 -*-

import time

from btsmapper.core.constants import BTSMAPPER_PATH

from peewee import SqliteDatabase, Model, RawQuery
from peewee import CharField, IntegerField, FloatField
from peewee import ForeignKeyField


class RSSdb(SqliteDatabase):
    """
    SQLite database object.
    """
    def connect(self):
        super(RSSdb, self).connect()
        pragma = RawQuery(BaseModel, "PRAGMA foreign_keys = ON;")
        self.execute(pragma)


class BaseModel(Model):
    """
    Basic database model, uses RSSdb as the database object.
    """
    class Meta:
        database = RSSdb("%s/core/results.db" % BTSMAPPER_PATH, check_same_thread=False)


class BTS(BaseModel):
    """
    BTS model.
    """
    op = CharField(max_length=256, null=True)
    lon = FloatField(null=True)
    lat = FloatField(null=True)
    cid = CharField(max_length=256, null=True)
    mcc = CharField(max_length=256, null=True)
    mnc = CharField(max_length=256, null=True)
    lac = CharField(max_length=256, null=True)
    date = IntegerField(default=int(time.mktime(time.localtime())))

    def __str__(self):
        return "<BTS '%s (%f:%f)'>" % (self.op, self.lon, self.lat)

    # def del_emails(self):
    #     deleted = 0
    #     for email in self.emails:
    #         deleted += email.delete_instance()
    #     return deleted
    #
    # @classmethod
    # def get_by_url(cls, url):
    #     return cls.select().where(
    #         cls.url == url
    #     ).get()
    #
    # @classmethod
    # def get_by_id(cls, id):
    #     return cls.select().where(
    #         cls.id == id
    #     ).get()
    #
    # @classmethod
    # def del_by_url(cls, url):
    #     feed = cls.get_by_url(url)
    #     del_emails = feed.emails.count()
    #     del_feeds = feed.delete_instance(recursive=True)
    #     return del_feeds, del_emails
    #
    # @classmethod
    # def del_by_id(cls, id):
    #     feed = cls.get_by_id(id)
    #     del_emails = feed.emails.count()
    #     del_feeds = feed.delete_instance(recursive=True)
    #     return del_feeds, del_emails

BTS.create_table(fail_silently=True)