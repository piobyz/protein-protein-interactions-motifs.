#!/usr/bin/env python
# encoding: utf-8

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import logging
import logging.config
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from sqlalchemy.exc import IntegrityError
from DBDIP import Interactors, Interactions

# logging.config.fileConfig("log/logconf.ini")
# log_load = logging.getLogger('motifkernel.loadData')

class DIPHandler(ContentHandler):

    def __init__(self, session):
        self.interactor_one = ''
        self.interactor_two = ''
        self.waiting_for_interactorRef_one = False
        self.waiting_for_interactorRef_two = False
        self.session = session

    def startElement(self, name, attributes):
        ##### INTERACTORS TABLE
        if name == 'interactor':
            self.id = attributes.get('id')
        if name == 'primaryRef' and attributes.get('db') == 'dip':
            self.dip_id = attributes.get('id')
        if name == 'secondaryRef' and attributes.get('db') == 'uniprot knowledge base':
                self.uniprot_id = attributes.get('id')

        ##### INTERACTIONS TABLE
        if name == 'interaction':
            self.id_interaction = attributes.get('id')
        if name == 'primaryRef' and attributes.get('db') == 'dip':
            self.dip_id_interaction = attributes.get('id')
        if name == 'participant':
            self.participant_id = attributes.get('id')
        if name == 'interactorRef' and self.participant_id=='1':
            self.waiting_for_interactorRef_one = True
        if name == 'interactorRef' and self.participant_id=='2':
            self.waiting_for_interactorRef_two = True

    def characters(self, data):
        if self.waiting_for_interactorRef_one:
            self.interactor_one = data
        elif self.waiting_for_interactorRef_two:
            self.interactor_two = data

    def endElement(self, name):
        ##### INTERACTORS TABLE
        if name == 'interactor':
            try:
                new_interactor = Interactors(id=self.id, dip_id=self.dip_id, uniprot_id=self.uniprot_id)
                self.session.add(new_interactor)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

        ##### INTERACTORS PROCESSING
        if name == 'participant':
            self.participant_id = 0
        if name == 'interactorRef':
            self.waiting_for_interactorRef_one = False
            self.waiting_for_interactorRef_two = False
        ##### INTERACTORS TABLE
        if name == 'interaction':
            try:
                new_interaction = Interactions(self.id_interaction, self.dip_id_interaction,
                    self.interactor_one, self.interactor_two)
                self.session.add(new_interaction)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()


def sax_parse(file_to_parse, DB_session):
    # SAX init
    sax_parser = make_parser()
    handler = DIPHandler(DB_session)
    sax_parser.setContentHandler(handler)

    sax_parser.parse(file_to_parse)

if __name__ == "__main__":
    'This module is supposed only to be imported.'
    # TODO insert tests here
