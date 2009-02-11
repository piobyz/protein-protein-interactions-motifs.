#!/usr/bin/env python
# encoding: utf-8

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from DBDIP import PDB, Interactors, Interactions


class DIPHandler(ContentHandler):

    def __init__(self):
        self.interactor_one = ''
        self.interactor_two = ''
        self.waiting_for_interactorRef_one = False
        self.waiting_for_interactorRef_two = False

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
                session.add(new_interactor)
                session.commit()
            except IntegrityError:
                session.rollback()

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
                session.add(new_interaction)
                session.commit()
            except IntegrityError:
                session.rollback()


def main():
    # SAX init
    parser = make_parser()
    handler = DIPHandler()
    parser.setContentHandler(handler)

    parser.parse(open('../Mmusc20090126.mif25'))


if __name__ == "__main__":
    meta = MetaData()
    Base = declarative_base(metadata=meta)

    # engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///DIP.db', echo=False)
    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    main()
