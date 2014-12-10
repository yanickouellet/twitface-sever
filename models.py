# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Ami(ndb.Model):
    noAmi1 = ndb.KeyProperty(kind='Membre', required=True)
    noAmi2 = ndb.KeyProperty(kind='Membre', required=True)
    dateAmite = ndb.DateProperty(required=True)


class DemandeAmi(ndb.Model):
    amiDate = ndb.DateProperty(required=True)
    noDemandeur = ndb.IntegerProperty(required=True)


class Membre(ndb.Model):
    nom = ndb.StringProperty(required=True)
    prenom = ndb.StringProperty(required=True)
    sexe = ndb.StringProperty(required=True)
    dateNaissance = ndb.DateProperty(required=True)
    villeOrigine = ndb.StringProperty(required=True)
    villeActuelle = ndb.StringProperty(required=True)
    courriel = ndb.StringProperty(required=True)
    nomUtil = ndb.StringProperty(required=True)
    motPasse = ndb.StringProperty(required=True)


class Publication(ndb.Model):
    texte = ndb.StringProperty(required=True)
    date = ndb.DateProperty(required=True)
    noCreateur = ndb.IntegerProperty(required=True)
    noBabillard = ndb.IntegerProperty(required=True)
