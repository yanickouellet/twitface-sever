# -*- coding: utf-8 -*-

import webapp2
import logging
import traceback
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication, DemandeAmi, Ami


class DemandeAmiHandler(webapp2.RequestHandler):
    def get(self, mem_no, dem_ami_no=None):
        try:
            cle_mem = ndb.Key('Membre', int(mem_no))
            if (cle_mem.get() is None):
                self.error(404)
                return

            list_dem_amis = []
            for dem in DemandeAmi.query(ancestor=cle_mem).fetch():
                dem_dict = dem.to_dict()
                dem_dict['no'] = dem.key.id()
                dem_dict['noInvite'] = cle_mem.id()
                list_dem_amis.append(dem_dict)

            json_data = json.dumps(list_dem_amis, default=serialiser_pour_json)

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

    def delete(self, mem_no, dem_ami_no):
        try:
            cle_mem = ndb.Key('Membre', int(mem_no))
            if (cle_mem.get() is None):
                self.error(404)
                return

            cle_dem_ami = ndb.Key('Membre', int(mem_no),
                                  'DemandeAmi', int(dem_ami_no))
            if (cle_dem_ami.get() is not None):
                cle_dem_ami.delete()
            else:
                ndb.delete_multi(DemandeAmi.query().fetch(keys_only=True))

            self.response.set_status(204)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)
        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)
