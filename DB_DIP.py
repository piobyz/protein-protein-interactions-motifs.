#!/usr/bin/env python
# encoding: utf-8
"""
This module contains XML parser for DIP's database flat file, mapper to SQLAlchemy classes and all methods connected with database maintaince. See :mod:`workflow` module for sample usage.
"""
__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Alpha"

import sys

import logging
import logging.config

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound

from Bio import SeqIO

# Logging configuration
logging.config.fileConfig("/Users/piotr/Projects/Thesis/Spring/PPIM/log/logging.conf")
log_load = logging.getLogger('load')

# TABLE Interactors, Interactions, PDB_UniProt, UniProtSeq
meta = MetaData()
Base = declarative_base(metadata=meta)


Structures = Table('Structures', meta,
    Column('id', Integer, primary_key=True, index=True),
    Column('interactor_id', Integer, ForeignKey('Interactors.id'), index=True),
    Column('PDB_UniProt_id', Integer, ForeignKey('PDB_UniProt.id'), index=True)
)

class Structure(object):
    """SQLAlchemy class. Map to Structures Table class.
    TABLE Structures
    
    * **interactor_id** Interactor ID as in Interactors TABLE.
    * **PDB_UniProt_id** PDB_UniProt ID as in PDB_UniProt TABLE.
    
    Relations:
    
    *  many-to-many Interactors ``*`` ``*`` PDB_UniProt
    """
    def __init__(self, interactor_id, PDB_UniProt_id):
        self.interactor_id = interactor_id
        self.PDB_UniProt_id = PDB_UniProt_id

mapper(Structure, Structures) 


class Interactors(Base):
    """SQLAlchemy class in declarative_base style.
    TABLE Interactors
    
    * **id** entry id.
    * **dip_id** id as provided by DIP.
    * **uniprot_id** Uniprot ID.
    * **pdb_id** PDB id.
    
    Relations:
    
    * **structures_entry** many-to-many Interactors ``*`` ``*`` PDB_UniProt
    """

    __tablename__ = 'Interactors'

    # TODO in order to change default attribute docstring comment like one below is needed
    # seems that it requires Sphinx > 0.4.2 -- overwrite EPD installation? Remember about dependency: Jinja
    #  http://sphinx.pocoo.org/ext/autodoc.html?highlight=attribute%20documentation
    # TODO or even better -- skip those (leave only descriptions in class docstring)
    #: **id** entry id.
    id = Column(Integer, primary_key=True, index=True)
    dip_id = Column(String, nullable=False, unique=True, index=True)
    uniprot_id = Column(String, nullable=False, unique=True, index=True)

    # many-to-many Interactors * * PDB_UniProt
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
    """SQLAlchemy class in declarative_base style.
    TABLE Interactions
    
    * **id** entry id.
    * **dip_id** id as provided by DIP.
    * **interactor_one** first interactor.
    * **interactor_two** second interactor.
    """
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
    """SQLAlchemy class in declarative_base style.
    TABLE PDB_Uniprot
    
    * **pdb** PDB id
    * **chain** PDB chain
    * **sequence** sequence retrieved based on uniprot ID
    * **uniprot** Uniprot ID
    """
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


class UniProtSeq(Base):
    """SQLAlchemy class in declarative_base style.
    TABLE UniProtSeq
    
    * **sequence** is DNA sequence for a corresponding *uniprot* ID.
    * **uniprot** is Uniprot ID.
    """
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


class DIPHandler(ContentHandler):
    """This is SAX handler of XML parser.
    
    * **session** is SQLAlchemy session that parser should use.
    """
    def __init__(self, session):
        self.interactor_one = ''
        self.interactor_two = ''
        self.waiting_for_interactorRef_one = False
        self.waiting_for_interactorRef_two = False
        self.session = session

    def startElement(self, name, attributes):
        """Detects start tag in XML tree by name and its attributes.

        * **name** name of XML node.
        * **attributes** all attributes for particular node.
        """
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
        """Helper method for getting content of particular XML node.

        * **data** contains data for particular XML node.
        """
        if self.waiting_for_interactorRef_one:
            self.interactor_one = data
        elif self.waiting_for_interactorRef_two:
            self.interactor_two = data

    def endElement(self, name):
        """Detects end tag and performs various actions with content of this tag.
        
        * **name** is name of closing tag.
        """
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
        ##### INTERACTIONS TABLE
        if name == 'interaction':
            try:
                new_interaction = Interactions(self.id_interaction, self.dip_id_interaction,
                    self.interactor_one, self.interactor_two)
                self.session.add(new_interaction)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

def get_session(db_name, verbose, test):
    """Returns current DB session from SQLAlchemy pool.
    
    * **db_name** name of databse to be created
    * **verbose** if *True* SQLAlchemy **echo** is set to *True*.
    * **test** if *True* database is crea   ted in RAM only.
    
    >>> get_session('Mmusc20090126', False, True) #doctest: +ELLIPSIS
    <sqlalchemy.orm.session.Session object at 0x...>
    
    >>> get_session('Mmusc20090126', False, False) #doctest: +ELLIPSIS
    <sqlalchemy.orm.session.Session object at 0x...>
    """
    if test:
        engine = create_engine('sqlite:///:memory:', echo=verbose)
        log_load.debug('DB in RAM.')
    else:
        engine = create_engine('sqlite:///' + 'DB/' + db_name + '.db', echo=verbose)
        log_load.debug('DB stored in file: %s' % 'DB/' + db_name + '.db')
    
    # Create TABLES: Structures, Interactions, Interactors, PDB_UniProt, UniProtSeq
    meta.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session


def sax_parse(file_to_parse, session):
    """Runs a SAX parser on file and saves results to DB using SQLAlchemy session.
    
    * **file_to_parse** XML file to be parsed
    * **session** is SQLAlchemy session that parser should use.
    """
    sax_parser = make_parser()
    handler = DIPHandler(session)
    sax_parser.setContentHandler(handler)

    sax_parser.parse(file_to_parse)


def pdb2uniprot(current_session):
    '''Create database with mapping between PDB+chain and UniProt id in Structures TABLE.
    Uses PDB_UniProt TABLE.
    Uses Structures TABLE.
    
    * **current_session** is SQLAlchemy session that this function should use.
    '''
    ################ PDB_UniProt TABLE ################
    try:
        mapping_file = open('external_datafiles/pdbsws_chain.txt')
    except IOError:
        log_load.exception('There is no file external_datafiles/pdbsws_chain.txt with PDB to UniProt mappings.')
            
    # All entries from mapping_file are processed but it's quicker than comparing each UniProt id
    # and insert only those present in Interactors.uniprot_id
    for line in mapping_file:
        arguments = line.split(' ')
        try:
            new_PDB_UniProt = PDB_UniProt(pdb=arguments[0], chain=arguments[1], uniprot=(arguments[2]).strip())
            current_session.add(new_PDB_UniProt)
            current_session.commit()
        except IntegrityError:
            current_session.rollback()
            log_load.exception('Entry: %s already exist in the DB' % new_PDB_UniProt)
    
    # Map UniProt ids from Interactors and PDB_UniProt in Structures TABLE.

    # Retrieve all proteins from Interactors Table, get their UniProt ids
    # and retrieve corresponding PDB name+chain from PDB_UniProt TABLE.
    # Finally, store relations in a Structures TABLE.
    query = current_session.query(Interactors).order_by(Interactors.id)
    all_interactors = query.all()
    for interactor in all_interactors:
        pdb_list = current_session.query(PDB_UniProt).filter(PDB_UniProt.uniprot==interactor.uniprot_id).all()
        if pdb_list:
            for pdb_item in pdb_list:
                interactor.structures_entry.append(pdb_item)
                current_session.commit()


def uniprot_sequence(current_session):
    """
    Creates separate DB with UniProt IDs and its sequences from uniprot_sprot.fasta (15.02.2009).

    WARNING: Not all sequences are present in this file.

    Uses PDB_UniProt.sequence TABLE.

    * **current_session** is SQLAlchemy session that this function should use.
    """
    try:
        mapping_file = open('external_datafiles/uniprot_sprot.fasta')
    except IOError:
        log_load.exception('File %s is not present.' % mapping_file)
        sys.exit(1)

    for cur_record in SeqIO.parse(mapping_file, "fasta"):
        title = str(cur_record.name).split('|')[1]
        seq = cur_record.seq.tostring()

        try:
            new_UniProtSeq = UniProtSeq(uniprot=title, sequence=seq)
            current_session.add(new_UniProtSeq)
            current_session.commit()
        except IntegrityError:
            current_session.rollback()
            log_load.exception('Entry: %s already exist in the UniProtSeq' % new_UniProtSeq)


def uniprot_sequence_transfer(current_session):
    """Fill sequence entry for each UniProt in Structures TABLE.
    
    Transfers sequences obtained from UniProtSeq TABLE to PDB_UniProt.

    * **current_session** is SQLAlchemy session that this function should use.
    """
    
    all_structures = current_session.query(Structures).all()
    for structure in all_structures:
        pdb_entry = current_session.query(PDB_UniProt).filter(PDB_UniProt.id==structure.PDB_UniProt_id).one()
        try:
            uniprot_seq = current_session.query(UniProtSeq.sequence).filter(UniProtSeq.uniprot==pdb_entry.uniprot).one()
            pdb_entry.sequence = uniprot_seq[0]
            # session.flush()
            current_session.commit()
        except NoResultFound:
            log_load.exception('No results for: %s' % pdb_entry.uniprot)


def both_interacting_from_DIP(current_session):
    """SQLAlchemy query returns a list with both interacting proteins (PDB|chain) from DIP database.
    
    * **current_session** is SQLAlchemy session that this function should use.
    
    SQL equivalent:
    
    .. code-block:: sql
    
        SELECT 
            PDB1.pdb, PDB1.chain,
            PDB2.pdb, PDB2.chain
        FROM Interactions,
            Interactors AS Int1, Interactors AS Int2,
            Structures AS Str1, Structures AS Str2,
            PDB_UniProt AS PDB1, PDB_UniProt AS PDB2
        WHERE (
            (Interactions.interactor_one=Int1.id)
            AND (Int1.id=Str1.interactor_id)
            AND (Str1.PDB_Uniprot_id=PDB1.id)
        ) 
        AND (
            (Interactions.interactor_two=Int2.id)
            AND (Int2.id=Str2.interactor_id)
            AND (Str2.PDB_Uniprot_id=PDB2.id)
        )
        GROUP BY Interactions.interactor_one, Interactions.interactor_two;
    """
    PDB1 = aliased(PDB_UniProt, name='PDB1')
    PDB2 = aliased(PDB_UniProt, name='PDB2')
    Int1 = aliased(Interactors, name='Int1')
    Int2 = aliased(Interactors, name='Int1')
    Str1 = aliased(Structure, name='Str1')
    Str2 = aliased(Structure, name='Str2')


    interactions_DIP = current_session.query(PDB1.pdb, PDB1.chain, PDB2.pdb, PDB2.chain).filter(Interactions.interactor_one==Int1.id).filter(Int1.id==Str1.interactor_id).filter(Str1.PDB_UniProt_id==PDB1.id).filter(Interactions.interactor_two==Int2.id).filter(Int2.id==Str2.interactor_id).filter(Str2.PDB_UniProt_id==PDB2.id).group_by(Interactions.interactor_one, Interactions.interactor_two).all()
    
    return interactions_DIP


def uniq(alist):
    """Returns non redundant list.
    
    * **alist** list to be processed.
    
    >>> uniq([(u'1e9z', u'A', u'1e9z', u'A'), (u'2zl4', u'N', u'1klx', u'A'), (u'1e9z', u'A', u'1e9z', u'A')])
    [(u'1e9z', u'A', u'1e9z', u'A'), (u'2zl4', u'N', u'1klx', u'A')]
    """
    set = {}
    return [set.setdefault(e, e) for e in alist if e not in set]


def create_reversed_interactions_removing_duplicates(dip_interactions_source):
    """Takes a list of interacting PDB1|chain1|PDB2|chain2 and appends PDB2|chain2|PDB1|chain1 finally removing duplicates and returs it.
    
    * **dip_interactions_source** a list with interacting proteins, format as described above, also, see doctest below.
    
    >>> create_reversed_interactions_removing_duplicates([(u'1e9z', u'A', u'1e9z', u'A'), (u'2zl4', u'N', u'1klx', u'A'), (u'1e9z', u'A', u'1e9z', u'A')])
    [u'1e9z|A|1e9z|A', u'2zl4|N|1klx|A', u'1klx|A|2zl4|N']
    """
    with_possible_duplicates = []

    # Because we need to consider interactions where 2 pdb+chain are listed also in the reverse order
    # we want to create a non redundant list with all interactions.
    for entry in dip_interactions_source:
        first_pdb = entry[0].strip()
        first_chain = entry[1].strip()
        second_pdb = entry[2].strip()
        second_chain = entry[3].strip()

        non_reversed_interaction = '%s|%s|%s|%s' % (first_pdb, first_chain, second_pdb, second_chain)
        reversed_interaction = '%s|%s|%s|%s' % (second_pdb, second_chain, first_pdb, first_chain)

        with_possible_duplicates.append(non_reversed_interaction)
        with_possible_duplicates.append(reversed_interaction)

    without_duplicates = uniq(with_possible_duplicates)
    log_load.info('Found %s duplicates.' % (len(with_possible_duplicates) - len(without_duplicates)))

    return without_duplicates


if __name__ == "__main__":
    try:
        import nose
        nose.main(argv=['', '--verbose', '--with-doctest', '--with-coverage', '--cover-inclusive', '--cover-package=PPIM', '--detailed-errors', '--with-profile'])
    except ImportError:
        raise Exception("This package uses nose module for testing (which you do not have installed).")
