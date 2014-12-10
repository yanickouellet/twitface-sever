# -*- coding: utf-8 -*-
import webapp2
import json

from google.appengine.ext import ndb
from models import Membre, Publication, DemandeAmi


class MembreHandler(webapp2.RequestHandler):
    def get(self, mem_no=None):
        try:
            if mem_no is None:
                list_membres = []
                requete = Membre.query()

                # Critères de recherche
                nom = self.request.get('nom')
                ville_origine = self.request.get('ville-origine')
                ville_actuelle = self.request.get('ville-actuelle')
                sexe = self.request.get('sexe')

                # Filtre
                if (nom != ''):
                    # TODO Même chose pour le membre
                    requete = requete.filter(Membre.nom == nom)
                    requete = requete.order(Membre.nom)
                if (ville_origine != ''):
                    requete = requete.filter(
                        Membre.villeOrigine == ville_origine)
                    requete = requete.order(Membre.villeOrigine)
                if (ville_actuelle != ''):
                    requete = requete.filter(
                        Membre.villeActuelle == ville_actuelle)
                    requete = requete.order(Membre.villeActuelle)
                if (sexe != ''):
                    requete = requete.filter(Membre.sexe == sexe)
                    requete = requete.order(Membre.sexe)

                requete = requete.order(Membre.prenom)

                #  Parcours des membres retournées par la requête.
                for mem in requete.fetch(limit=20):
                    mem_dict = mem.to_dict()
                    mem_dict["no"] = mem.key.id()
                    list_membres.append(mem_dict)
                json_data = json.dumps(list_membres,
                                       default=serialiser_pour_json)

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

