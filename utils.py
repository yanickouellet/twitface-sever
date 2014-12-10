# -*- coding: utf-8 -*-

def serialiser_pour_json(objet):
    if isinstance(objet, datetime.datetime):
        return objet.replace(microsecond=0).isoformat()
    elif isinstance(objet, datetime.date):
        return objet.isoformat()
    else:
        return objet
