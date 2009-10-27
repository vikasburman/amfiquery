# -*- coding: utf-8 -*-

from google.appengine.ext import db

class MFInfo(db.Model):
    """ Model class for a Mutual Fund quote """

    scheme_code = db.StringProperty(required = True)
    scheme_name = db.StringProperty(required = True)
    nav = db.StringProperty(required = True)
    repurchase_price = db.StringProperty(required = True)
    sale_price = db.StringProperty(required = True)
    date = db.StringProperty(required = True)
