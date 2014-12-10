# -*- coding: utf-8 -*-
import webapp2
import json
import datetime

from google.appengine.ext import ndb
from models import Membre, Publication, DemandeAmi, Ami

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
            cle1 = ndb.Key('Membre', int(ami["MemNo1"]))
            cle2 = ndb.Key('Membre', int(ami["MemNo2"]))
            a = Ami(noAmi1=cle1,
                    noAmi2=cle2,
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

