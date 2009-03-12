#!/usr/bin/env python
# encoding: utf-8

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import sys
import os
from optparse import OptionParser
import logging
import logging.config
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
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


def main():
    usage="""
This is a part of the package for String Kernel Classification using SVM.
Written by Piotr Byzia (piotr.byzia@gmail.com).
Credits: Hugh Shanahan, Royal Holloway University of London.
Licence: ...

Usage: %prog [options] *.mif25
"""
    parser = OptionParser(usage=usage, version="%prog 0.1.0")
    parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Test mode: DB in RAM only!! [default: %default]")
    parser.add_option("-e", "--echo", action="store_true", dest="echo", default=False, help="Echo for DB: True or False [default: %default]")

    (options, args) = parser.parse_args()
    if(len(args) != 1):
        parser.print_help()
        sys.exit(1)
    
    try:
        input_file = open(args[0])
    except IOError:
        # log_load.exception('There is no such a file: %s' % options.input)
        sys.exit(1)
    
    file_name = os.path.basename(args[0]).split('.')[0]

    if options.test:
        engine = create_engine('sqlite:///:memory:', echo=options.echo)
        # log_load.info('DB in RAM.')
    else:
        engine = create_engine('sqlite:///' + 'DB/' + file_name + '.db', echo=options.echo)
        # log_load.info('DB stored in file: %s' % 'DB/' + file_name + '.db')
        # FIXME Find out how to initiate mapper class in DBDIP.py with parameter so that created file with DB
        # has the same name as this one above.

    Session = sessionmaker(bind=engine)
    session = Session()

    # SAX init
    sax_parser = make_parser()
    handler = DIPHandler(session)
    sax_parser.setContentHandler(handler)

    sax_parser.parse(open(args[0]))


if __name__ == "__main__":
    main()
