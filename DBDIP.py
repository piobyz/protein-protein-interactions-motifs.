#!/usr/bin/env python
# encoding: utf-8
"""
SQLAlchemy mappers for DIP module.
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import sys
import os

from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from optparse import OptionParser

from Bio import SeqIO

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import relation, backref, join, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import DIP


# TABLE Interactors, Interactions, PDB_UniProt
meta = MetaData()
Base = declarative_base(metadata=meta)

# TABLE UniProtSeq
meta_uniprot = MetaData()
Base_Uniprot = declarative_base(metadata=meta_uniprot)


Structures = Table('Structures', meta,
    Column('interactor_id', Integer, ForeignKey('Interactors.id'), index=True),
    Column('PDB_UniProt_id', Integer, ForeignKey('PDB_UniProt.id'), index=True)
)


class Interactors(Base):
    __tablename__ = 'Interactors'

    id = Column(Integer, primary_key=True, index=True)
    dip_id = Column(String, nullable=False, unique=True, index=True)
    uniprot_id = Column(String, nullable=False, unique=True, index=True)

    # many-to-many Interactors * * PDB
    structures_entry = relation('PDB_UniProt', secondary=Structures)

    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        if 'id' in kw:
            self.id = kw['id']
        if 'dip_id' in kw:
            self.dip_id = kw['dip_id']
        if 'uniprot_id' in kw:
            self.uniprot_id = kw['uniprot_id']
        if 'pdb_id' in kw:
            self.pdb_id = kw['pdb_id']

    def __repr__(self):
        return "<Interactors('%s', '%s')>" % (self.id, self.dip_id)


class Interactions(Base):
    __tablename__ = 'Interactions'

    id = Column(Integer, primary_key=True, index=True)
    dip_id = Column(String, nullable=False, index=True)
    interactor_one = Column(String, nullable=False, index=True)
    interactor_two = Column(String, nullable=False, index=True)

    def __init__(self, id, dip_id, interactor_one, interactor_two):
        self.id = id
        self.dip_id = dip_id
        self.interactor_one = interactor_one
        self.interactor_two = interactor_two

    def __repr__(self):
        return "<Interactions(%s, %s)>" % (self.id, self.dip_id)


class PDB_UniProt(Base):
    __tablename__ = 'PDB_UniProt'

    id = Column(Integer, primary_key=True, index=True)
    pdb = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    sequence = Column(String)
    uniprot = Column(String, nullable=False, index=True)
    
    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        if 'pdb' in kw:
            self.pdb = kw['pdb']
        if 'chain' in kw:
            self.chain = kw['chain']
        if 'sequence' in kw:
            self.sequence = kw['sequence']
        if 'uniprot' in kw:
            self.uniprot = kw['uniprot']

    def __repr__(self):
        return "<PDB_UniProt('%s|%s', '%s')>" % (self.pdb, self.chain, self.uniprot)


class UniProtSeq(Base_Uniprot):
    __tablename__ = 'UniProtSeq'

    id = Column(Integer, primary_key=True, index=True)
    uniprot = Column(String, nullable=False, index=True)
    sequence = Column(String, nullable=False)

    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        if 'sequence' in kw:
            self.sequence = kw['sequence']
        if 'uniprot' in kw:
            self.uniprot = kw['uniprot']

    def __repr__(self):
        return "<UniProtSeq('%s|%s')>" % (self.uniprot, self.sequence)


def pdb2uniprot(current_session):
    ################ PDB_UniProt TABLE ################
    try:
        mapping_file = open('../pdbsws_chain.txt')
    except IOError:
        log_load('There is no file ../pdbsws_chain.txt with PDB to UniProt mappings.')
        print 'There is no file ../pdbsws_chain.txt with PDB to UniProt mappings.'
        
    
    for line in mapping_file:
        arguments = line.split(' ')
        try:
            new_PDB_UniProt = PDB_UniProt(pdb=arguments[0], chain=arguments[1], uniprot=(arguments[2]).strip())
            current_session.add(new_PDB_UniProt)
            current_session.commit()
        except IntegrityError:
            current_session.rollback()
            # log_db.exception('Entry: %s already exist in the DB' % new_PDB_UniProt)
            print 'Entry: %s already exist in the DB' % new_PDB_UniProt


def uniprot_sequence(current_session, current_session_uniprot):
    ################ PDB_UniProt.sequence TABLE ################
    # 1. Creates a separate DB with UniProt IDs and its sequences (uniprot_sprot.fasta) on 15.02.2009
    # 2. Transfers sequences obtained from UniProtSeq TABLE
    # WARNING: Not all sequences are present in this file.
    
    mapping_file = open('../uniprot_sprot.fasta')

    for cur_record in SeqIO.parse(mapping_file, "fasta"):
        title = str(cur_record.name).split('|')[1]
        seq = cur_record.seq.tostring()

        try:
            new_UniProtSeq = UniProtSeq(uniprot=title, sequence=seq)
            current_session_uniprot.add(new_UniProtSeq)
            current_session_uniprot.commit()
        except IntegrityError:
            current_session_uniprot.rollback()
            # log_db.exception('Entry: %s already exist in the UniProtSeq' % new_UniProtSeq)
            print 'Entry: %s already exist in the UniProtSeq' % new_UniProtSeq

    # Fill sequence entry for each UniProt in Structures TABLE
    all_structures = current_session.query(Structures).all()
    for structure in all_structures:
        pdb_entry = current_session.query(PDB_UniProt).filter(PDB_UniProt.id==structure.PDB_UniProt_id).one()
        try:
            uniprot_seq = current_session_uniprot.query(UniProtSeq.sequence).filter(UniProtSeq.uniprot==pdb_entry.uniprot).one()
            pdb_entry.sequence = uniprot_seq[0]
            # session.flush()
            current_session_uniprot.commit()
        except NoResultFound:
            # log_db.exception(''No results for: %s' % pdb_entry.uniprot)
            print 'No results for: %s' % pdb_entry.uniprot


def main():
    usage="""
This is a part of the package for String Kernel Classification using SVM.
Written by Piotr Byzia (piotr.byzia@gmail.com).
Credits: Hugh Shanahan, Royal Holloway University of London.
Licence: ...

Usage: %prog [options] *.mif25

Required files:
1. *.mif25 files (http://dip.doe-mbi.ucla.edu/dip/Download.cgi?SM=7)
2. pdbsws_chain.txt (http://www.bioinf.org.uk/pdbsws/)
3. uniprot_sprot.fasta (Uniprot's FTP)
"""
    parser = OptionParser(usage=usage, version="%prog 0.1.0")
    parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Test mode: DB in RAM only!! [default: %default]")
    parser.add_option("-e", "--echo", action="store_true", dest="echo", default=False, help="Echo for DBs: True or False [default: %default]")
    parser.add_option("-u", "--uniprot", action="store_true", dest="uniprot", default=False, help="Run UniProt to PDB mapping [default: %default]")
    parser.add_option("-s", "--uniseq", action="store_true", dest="uniseq", default=False, help="Transfer sequences for each UniProt id from fasta file [default: %default]")

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

    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # SAX parsing the *.mif25 file and putting it into DB
    # DIP.sax_parse(input_file, session)
    
    if options.uniprot or options.uniseq:
        if options.test:
            engine_uniprot = create_engine('sqlite:///:memory:', echo=options.echo)
        else:
            engine_uniprot = create_engine('sqlite:///DB/UniProt_Seq.db', echo=options.echo)

        Session_uniprot = sessionmaker(bind=engine_uniprot)
        session_uniprot = Session_uniprot()
        meta_uniprot.create_all(engine_uniprot)

        if options.uniprot:
            # Complete PDB_UniProt with mappings between PDB-chain and UniProt
            pdb2uniprot(session)
            # log_load.info('PDB to UniProt mapping has been applied in this run.')
        if options.uniseq:
            # Feed the PDB_UniProt TABLE with sequences for each UniProts
            uniprot_sequence(session, session_uniprot)
            # log_load.info('Sequences for each UniProt has been applied in this run.')
            print 'DB created.'
    else:
        # log_load.info('PDB to UniProt mapping has NOT been applied in this run.')
        print 'UniProt mapping NOT applied.'
if __name__ == '__main__':
    main()
