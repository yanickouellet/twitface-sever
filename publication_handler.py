# -*- coding: utf-8 -*-

import webapp2
import logging
import traceback
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication, DemandeAmi


class PublicationHandler(webapp2.RequestHandler):
    def put(self, pub_no):
        try:
            cle = ndb.Key("Publication", int(pub_no))
            pub = cle.get()
            pub_json = json.loads(self.request.body)

            if pub is None:
                status = 201
                pub = Publication(key=cle)
            else:
                if int(pub_json['noCreateur']) == int(pub.noCreateur):
                    status = 200
                    pub.texte = str(pub_json['texte'])
                    pub.date = datetime.datetime.strptime(pub_json["date"],
                                                          '%Y-%m-%d')
                    pub.noBabillard = int(pub_json['noCreateur'])
                    pub.put()
                else:
                    status = 400
                    return

            pub_dict = pub.to_dict()
            pub_dict["no"] = pub.key.id()
            pub_json = json.dumps(pub_dict, default=serialiser_pour_json)

            self.response.set_status(status)
            self.response.headers['Content-Type'] = ('application/json;' +
                                                     ' charset=utf-8')
            self.response.out.write(pub_json)

        # Exceptions en lien avec les données fournies.
        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        # Exceptions graves lors de l'exécution du code.
        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)

    def get(self, pub_no):
        try:
            cle = ndb.Key('Publication', int(pub_no))
            pub = cle.get()

            if (pub is None):
                self.error(404)
                return

            pers_dict = pub.to_dict()
            pers_dict["no"] = pub.key.id()
            json_data = json.dumps(pers_dict, default=serialiser_pour_json)

            self.response.set_status(200)
            self.response.headers['Content-Type'] = ('application/json;' +
                                                     ' charset=utf-8')
            self.response.out.write(json_data)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)

    def delete(self, pub_no):
        try:
            cle = ndb.Key('Publication', int(pub_no))
            if cle.get() is not None:
                cle.delete()
            else:
                self.error(404)
                return

            self.response.set_status(204)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)

    def post(self, pub_no=None):
        try:
            pub = Publication()
            pub_json = json.loads(self.request.body)
            pub.no_babillard = int(pub_json['noBabillard'])
            pub.texte = pub_json['texte']
            pub.date = datetime.datetime.strptime(pub_json['date'], '%Y-%m-%d')
            pub.noBabillard = int(pub_json['noBabillard'])
            pub.noCreateur = int(pub_json['noCreateur'])
            cle_pub = pub.put()

            self.response.set_status(201)
            self.response.headers['Location'] = (self.request.url +
                                                 '/' + str(cle_pub.id()))
            self.response.headers['Content-Type'] = ('application/json;' +
                                                     ' charset=utf-8')
            pub_dict = pub.to_dict()
            pub_dict["no"] = pub.key.id()
            pub_json = json.dumps(pub_dict, default=serialiser_pour_json)
            self.response.out.write(pub_json)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)
        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)
