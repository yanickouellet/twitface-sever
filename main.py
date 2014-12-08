# -*- coding: utf-8 -*-

import webapp2
import logging
import traceback
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication, DemandeAmi, Ami


def serialiser_pour_json(objet):
    if isinstance(objet, datetime.datetime):
        return objet.replace(microsecond=0).isoformat()
    elif isinstance(objet, datetime.date):
        return objet.isoformat()
    else:
        return objet


class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.response.out.write('TP5 - Maxime Trottier et Yanick Ouellet')


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
                    # TODO
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


class AmiHandler(webapp2.RequestHandler):
    def get(self, mem_no):
        try:
            cle_mem = ndb.Key('Membre', int(mem_no))
            if (cle_mem.get() is None):
                self.error(404)
                return

            requete = Ami.query().filter(ndb.OR(Ami.noAmi1 == cle_mem.id(),
                                                Ami.noAmi2 == cle_mem.id()))

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

    # def post(self, mem_no, ami_no):


class DataResetHandler(webapp2.RequestHandler):
    def post(self):
        with open("twitface.json") as json_file:
            json_data = json.load(json_file)
        ndb.delete_multi(Membre.query().fetch(keys_only=True))
        ndb.delete_multi(DemandeAmi.query().fetch(keys_only=True))
        ndb.delete_multi(Ami.query().fetch(keys_only=True))
        ndb.delete_multi(Publication.query().fetch(keys_only=True))

        lst_membre = []
        lst_demande_ami = []
        lst_publication = []
        lst_ami = []

        for membre in json_data["membres"]:
            cle = ndb.Key("Membre", int(membre["MemNo"]))
            m = Membre(key=cle,
                       nom=membre["MemNom"].split(' ')[1],
                       prenom=membre["MemNom"].split(' ')[0],
                       sexe=membre["MemSexe"],
                       dateNaissance=datetime.datetime.strptime(
                           membre["MemDateNaissance"], '%Y-%m-%d'),
                       villeOrigine=membre["MemVilleOrigine"],
                       villeActuelle=membre["MemVilleActuelle"],
                       courriel=membre["MemCourriel"],
                       nomUtil=membre["MemNomUtil"],
                       motPasse=membre["MemMotPasse"])
            lst_membre.append(m)

        for ami in json_data["amis"]:
            a = Ami(noAmi1=int(ami["MemNo1"]),
                    noAmi2=int(ami["MemNo2"]),
                    dateAmite=datetime.datetime.strptime(
                        ami["DateAmitie"], '%Y-%m-%d'))
            lst_membre.append(a)

        for demAmi in json_data["demandesAmis"]:
            cle = ndb.Key("Membre", int(demAmi["MemNoInvite"]),
                          "DemandeAmi", int(demAmi["DemAmiNo"]))
            d = DemandeAmi(key=cle,
                           noDemandeur=int(demAmi["MemNoDemandeur"]),
                           amiDate=datetime.datetime.strptime(
                               demAmi["DemAmiDate"], '%Y-%m-%d'))
            lst_membre.append(d)

        for pub in json_data["publications"]:
            cle = ndb.Key("Publication", int(pub["PubNo"]))
            p = Publication(key=cle,
                            texte=pub["PubTexte"],
                            noCreateur=int(pub["MemNoCreateur"]),
                            noBabillard=int(pub["MemNoBabillard"]),
                            date=datetime.datetime.strptime(
                                pub["PubDate"], '%Y-%m-%d'))
            lst_membre.append(p)

        ndb.put_multi(lst_membre)
        ndb.put_multi(lst_demande_ami)
        ndb.put_multi(lst_publication)
        ndb.put_multi(lst_ami)

        self.response.set_status(200)

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/', handler=MainPageHandler, methods=['GET']),
        webapp2.Route(r'/publications', handler=PublicationHandler,
                      methods=['POST']),
        webapp2.Route(r'/publications/<pub_no>', handler=PublicationHandler,
                      methods=['GET', 'PUT', 'DELETE']),
        webapp2.Route(r'/membres', handler=MembreHandler, methods=['GET']),
        webapp2.Route(r'/membres/<mem_no>/amis',
                      handler=AmiHandler, methods=['GET', 'POST']),
        webapp2.Route(r'/membres/<mem_no>/demandes_amis',
                      handler=DemandeAmiHandler, methods=['GET']),
        webapp2.Route(r'/membres/<mem_no>/demandes_amis/<dem_ami_no>',
                      handler=DemandeAmiHandler, methods=['DELETE']),
        webapp2.Route(r'/data/reset', handler=DataResetHandler,
                      methods=['POST']),
    ],
    debug=True)
