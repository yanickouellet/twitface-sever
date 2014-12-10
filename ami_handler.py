# -*- coding: utf-8 -*-

import webapp2
import logging
import traceback
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Ami
from utils import serialiser_pour_json

class AmiHandler(webapp2.RequestHandler):
    def get(self, mem_no):
        try:
            cle_mem = ndb.Key('Membre', int(mem_no))
            if (cle_mem.get() is None):
                self.error(404)
                return

            requete = Ami.query().filter(ndb.OR(Ami.noAmi1 == cle_mem,
                                                Ami.noAmi2 == cle_mem))

            list_amis = []
            for ami in requete.fetch():
                ami_dict = ami.to_dict()
                ami_dict["no"] = ami.key.id()
                list_amis.append(ami_dict)

            json_data = json.dumps(list_amis, default=serialiser_pour_json)

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

    def post(self, mem_no):
        try:
            json_body = json.loads(self.request.body)

            no_membre = int(mem_no)
            no_ami = int(json_body['ami_no'])

            if (no_membre != json_body['membre_no']):
                self.error(400)
                return

            cle_mem = ndb.Key('Membre', no_membre)
            cle_ami = ndb.Key('Membre', no_ami)

            if (cle_mem.get() is None):
                self.error(404)
                return
            if (cle_ami.get() is None):
                self.error(400)
                return

            requete = Ami.query().filter(ndb.AND(
                ndb.OR(
                    Ami.noAmi1 == no_ami
                )
            ))

            ami = Ami(noAmi1=no_membre,
                      noAmi2=no_ami,
                      dateAmite=datetime.datetime.now())
            ami.put()
            ami_dict = ami.to_dict()
            ami_dict['no'] = ami.key.id()
            logging.error("%s", ami_dict)
            json_data = json.dumps(ami_dict, default=serialiser_pour_json)

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
