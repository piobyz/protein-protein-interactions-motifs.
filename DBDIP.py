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
import os.path # os.path.exists

from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from optparse import OptionParser

from Bio import SeqIO

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relation, backref, join, sessionmaker
from sqlalchemy.orm import mapper
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.sql.expression import func

import DIP
from DB_3DID import PDB, Interacting_PDBs, parse_3did

# TABLE Interactors, Interactions, PDB_UniProt
meta = MetaData()
Base = declarative_base(metadata=meta)

# TABLE UniProtSeq
meta_uniprot = MetaData()
Base_Uniprot = declarative_base(metadata=meta_uniprot)

# TABLE UniProtSeq
meta_3DID = MetaData()
Base_3DID = declarative_base(metadata=meta_3DID)


Structures = Table('Structures', meta,
    Column('interactor_id', Integer, ForeignKey('Interactors.id'), primary_key=True, index=True),
    Column('PDB_UniProt_id', Integer, ForeignKey('PDB_UniProt.id'), index=True)
)


class Structure(object):
    def __init__(self, interactor_id, PDB_UniProt_id):
        self.interactor_id = interactor_id
        self.PDB_UniProt_id = PDB_UniProt_id


mapper(Structure, Structures) 


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
    '''Create database with mapping between PDB+chain and UniProt id.'''
    ################ PDB_UniProt TABLE ################
    try:
        mapping_file = open('../pdbsws_chain.txt')
    except IOError:
        # log_load('There is no file ../pdbsws_chain.txt with PDB to UniProt mappings.')
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
            print 'Entry: %s already exists in the DB' % new_PDB_UniProt


def uniprot_sequence(current_session, current_session_uniprot):
    ################ PDB_UniProt.sequence TABLE ################
    # 1. Create separate DB with UniProt IDs and its sequences (uniprot_sprot.fasta) on 15.02.2009
    # 2. Transfers sequences obtained from UniProtSeq TABLE to PDB_UniProt
    # WARNING: Not all sequences are present in this file.
    
    try:
        mapping_file = open('../uniprot_sprot.fasta')
    except IOError:
        print 'File %s is not present.' % mapping_file
        # log_load.excepttion('File %s is not present.' % mapping_file)
        # FIXME continue the script ommiting this analysis or exit(1)??

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


def uniq(alist):
    """Given alist returns non redundant list."""
    set = {}
    return [set.setdefault(e, e) for e in alist if e not in set]


def create_reversed_interactions_removing_duplicates(dip_interactions_source):
    """Takes a list of interacting PDB1|chain1|PDB2|chain2 and appends PDB2|chain2|PDB1|chain1
    finally removing duplicates."""
    with_possible_duplicates = []

    # Because we need to consider interactions where 2 pdb+chain are listed also in the reverse order
    # we want to create a non redundant list with all interactions.
    for entry in dip_interactions_source:
        first_pdb = entry[0].strip()
        first_chain = entry[1].strip()
        second_pdb = entry[2].strip()
        second_chain = entry[3].strip()

        non_reversed_interaction = '%s|%s|%s|%s\n' % (first_pdb, first_chain, second_pdb, second_chain)
        reversed_interaction = '%s|%s|%s|%s\n' % (second_pdb, second_chain, first_pdb, first_chain)

        with_possible_duplicates.append(non_reversed_interaction)
        with_possible_duplicates.append(reversed_interaction)

    without_duplicates = uniq(with_possible_duplicates)
    print 'Found %s duplicates.' % (len(with_possible_duplicates) - len(without_duplicates))
    # log_db.info('Found %s duplicates.' % (len(with_possible_duplicates) - len(without_duplicates)))

    return without_duplicates


def compare_interactions(dip_interactions_source=None, three_did_interactions_source=None, jena_interactions_source=None, \
                            jena=False):
    """Take interactions from one set (DIP, 3DID or JENA) and find overlapping interactions in the other."""
    dip_interactions = {}
    three_did_interactions = {}
    jena_interactions = {}

    # JENA has only PDB ids - without chains!!
    # Final results will be written here
    # try:
    #     results_handler = open(dip_interactions_source + '-overlapping.fa', 'w')
    # except IOError:
    #     # log_something.exception('Problems with creating file: %s' % results_handler)
    #     print 'Problems with creating file: %s' % results_handler

    if dip_interactions_source:
        number_of_dip_interactions = 0
        if jena:
            for entry in dip_interactions_source:
                # Take only PDB ids, without chains
                dip_interactions[entry[0]] = ''
                dip_interactions[entry[2]] = ''
                number_of_dip_interactions += 2
            else:
                for entry in dip_interactions_source:
                    dip_interactions[entry] = ''
                    number_of_dip_interactions += 1

    if three_did_interactions_source:
        number_of_3did_interactions = 0
        if jena:
            for entry in three_did_interactions_source:
                # Take only PDB ids, without chains
                three_did_interactions[entry[0]]=''
                three_did_interactions[entry[2]]=''
                number_of_3did_interactions += 2

    if jena_interactions_source:
        number_of_jena_interactions
        for entry in jena_interactions_source:
            jena_interactions[entry] = ''
            number_of_jena_interactions += 1
    
    if jena:
        # Find overlaps in DIP and JENA
        overlapping_dip_jena = 0
        for k in jena_interactions.keys():
            if k in dip_interactions.keys():
                to_write = '> %s\n' % k
                print to_write
                overlapping_dip_jena += 1

        # Find overlaps in 3DID and JENA
        overlapping_3did_jena = 0
        for k in jena_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n' % k
                print to_write
                overlapping_3did_jena += 1

    else:
        # Find overlaps in DIP and 3DID
        overlapping_dip_3did = 0
        for k in dip_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n%s\n' % (k, three_did_interactions[k])
                print to_write
                overlapping_dip_3did += 1
        
                # results_handler.write(to_write)
                # TODO write it to *.fa file and pass it to MotifKernel module
                # TODO log overlapping_dip_3did, etc.

    # results_handler.close()
    # log_results.info('Results written to: %s' % results_handler.name)
    # print 'Results written to: %s' % results_handler.name


def main():
    usage="""
This is a part of the package for String Kernel Classification
for Protein-Protein Interactions using SVM.
Written by Piotr Byzia (piotr.byzia@gmail.com).
Credits: Hugh Shanahan, Royal Holloway University of London.
Licence: ...

Usage: %prog [options] *.mif25

Required files:
1. *.mif25 files (http://dip.doe-mbi.ucla.edu/dip/Download.cgi?SM=7)
2. pdbsws_chain.txt (http://www.bioinf.org.uk/pdbsws/)
3. uniprot_sprot.fasta (Uniprot's FTP)
4. 3did_flat_Feb_15_2009.dat (http://gatealoy.pcb.ub.es/3did/download/3did_flat.gz)
5. Manually prepared JENA files, with PDB ids assigned to a particular species. (http://.....)
# TODO create dir external_files/ for those? It should be possible to specify ath to those file
by options

Databases (DB/ directory):
1. DIP *.mif25 based, e.g. Mmusc20090126.db (schema: doc/DIP_schema.pdf)
2. UniProt_Seq.db (PDB_UniProt TABLE + UniProtSeq TABLE) [only ONE needed for all *.mif25 DBs]
3. 3did.db [only ONE needed for all *.mif25 DBs] (schema: doc/3DID_schema.pdf)

# TODO Ad.2 only one, but for each species (because of the mapping - separate this step)...??
       Ad.3 only one?

Note:   Those databases will be created after first run (chose options to specify
        which one you need).
        If UniProt_Seq.db and 3did.db already exist in DB/ they won't be created
        unless forced to (see options).

Warning: Whole process takes about ...mins on MacBook Pro C2D 2.5GHz with 2GB RAM.

Results are stored in results/ .

See documentation in doc/ (HTML and PDF).

Run tests in tests/ .
"""
    parser = OptionParser(usage=usage, version="%prog 0.1.0")
    parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Test mode: DB in RAM only!!. [default: %default]")
    parser.add_option("-e", "--echo", action="store_true", dest="echo", default=False, help="Echo for DBs: True or False. [default: %default]")
    parser.add_option("-u", "--uniprot", action="store_true", dest="uniprot", default=False, help="Run UniProt to PDB mapping. [default: %default]")
    parser.add_option("-s", "--uniseq", action="store_true", dest="uniseq", default=False, help="Transfer sequences for each UniProt id from fasta file. [default: %default]")
    parser.add_option("-d", "--3did", action="store_true", dest="did", default=False, help="Parse 3DID flat file. [default: %default]")
    parser.add_option("-c", "--compare", action="store_true", dest="compare", default=False, help="Compare set of PDBs from single species between DIP, 3DID and JENA. [default: %default]")
    parser.add_option("-j", "--jena", action="store_true", dest="jena", help="Provide path to the correct JENA dataset (JENA/...). [default: %default]")
    parser.add_option("-l", "--clean", action="store_true", dest="clean", default=False, help="Clean all temp files unless something gone wrong. [default: %default]")
    parser.add_option("-m", "--most", action="store_true", dest="most", default=False, help="Prepare fasta file for the most interacting pair of domains from 3DID. Specify which pair should it be (1st, 2nd, ... most). [default: %default]")
    # TODO --jena: change attributes to get a file name not True/False
    # TODO --did: change attributes to get a file name not True/False
    # TODO --most: change attributes to get a number which most inter to calculate
    # TODO Implement clean.

    (options, args) = parser.parse_args()
    if(len(args) != 1):
        parser.print_help()
        sys.exit(1)
    # TODO maybe no arguments are needed? In case when sb wants to create a 3DID DB only?
    
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
    # TODO In case when sb wants to create a 3DID DB only the step above is not necessary.
    
    # TODO For TEST purpose only
    # engine = create_engine('sqlite:///../DB/DIP-species/DIP-Hpylo-test.db', echo=False)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # SAX parsing DIP's *.mif25 file and putting it into <species+date>.db
    # DIP.sax_parse(input_file, session)
    
    if options.uniprot or options.uniseq:
        # TODO This should be done rather like this: user specify what needs to be done
        #       and script takes care with DB it needs to connect, so DB connections should be run from
        #       'features defs'
        if options.test:
            engine_uniprot = create_engine('sqlite:///:memory:', echo=options.echo)
        else:
            engine_uniprot = create_engine('sqlite:///DB/UniProt_Seq.db', echo=options.echo)

        Session_uniprot = sessionmaker(bind=engine_uniprot)
        session_uniprot = Session_uniprot()
        meta_uniprot.create_all(engine_uniprot)

        if options.uniprot:
            # Create PDB_UniProt with mappings between each PDB+chain and UniProt
            pdb2uniprot(session)
            # log_load.info('PDB to UniProt mapping DB has been created.')
        if options.uniseq:
            # Feed the PDB_UniProt TABLE with sequences for each UniProt
            # FIXME Not sure if this should be a sepate step OR *always* connected with the one above
            uniprot_sequence(session, session_uniprot)
            # log_load.info('Sequence for each UniProt has been transfered.')
            print 'UniProt_Seq DB created and filled with sequences.'
    else:
        # log_load.info('PDB to UniProt mapping has NOT been applied in this run.')
        print 'UniProt_Seq NOT created (i.e. NO mappings and sequences).'
    
    if options.did or options.compare or options.most:
        if options.test:
            engine_3DID = create_engine('sqlite:///:memory:', echo=options.echo)
        else:
            engine_3DID = create_engine('sqlite:///DB/3did.db', echo=options.echo)

        Session_3DID = sessionmaker(bind=engine_3DID)
        session_3DID = Session_3DID()

    if options.did:
        # Creates DB with 3DID interactions (schema: doc/3DID_schema.pdf)
        # TODO check if that DB already exist, if yes -- skip the creation
        did_TEMP = '../3did_flat_Feb_15_2009.dat'
        parse_3did(did_TEMP, engine_3DID)
        # log_load.info('3DID flat file has been parsed and data inserted into DB.')
        print '3DID parsed.'
    else:
        # log_load.info('3DID data has not been created/updated due to options set.')
        print '3DID NOT parsed.'
    
    if options.compare:
        # Retrieve both interacting PDB|chain from DIP
        #
        # DIP-both_interacting-detailed.sql:
        # .output Hpylo-test.output
        # SELECT 
        #     PDB1.pdb, PDB1.chain,
        #     PDB2.pdb, PDB2.chain
        # FROM Interactions,
        #     Interactors AS Int1, Interactors AS Int2,
        #     Structures AS Str1, Structures AS Str2,
        #     PDB_UniProt AS PDB1, PDB_UniProt AS PDB2
        # WHERE (
        #     (Interactions.interactor_one=Int1.id)
        #     AND (Int1.id=Str1.interactor_id)
        #     AND (Str1.PDB_Uniprot_id=PDB1.id)
        # ) 
        # AND (
        #     (Interactions.interactor_two=Int2.id)
        #     AND (Int2.id=Str2.interactor_id)
        #     AND (Str2.PDB_Uniprot_id=PDB2.id)
        # )
        # GROUP BY Interactions.interactor_one, Interactions.interactor_two;
        PDB1 = aliased(PDB_UniProt, name='PDB1')
        PDB2 = aliased(PDB_UniProt, name='PDB2')
        Int1 = aliased(Interactors, name='Int1')
        Int2 = aliased(Interactors, name='Int1')
        Str1 = aliased(Structure, name='Str1')
        Str2 = aliased(Structure, name='Str2')
    

        interactions_DIP = session.query(PDB1.pdb, PDB1.chain, PDB2.pdb, PDB2.chain).filter(Interactions.interactor_one==Int1.id).filter(Int1.id==Str1.interactor_id).filter(Str1.PDB_UniProt_id==PDB1.id).filter(Interactions.interactor_two==Int2.id).filter(Int2.id==Str2.interactor_id).filter(Str2.PDB_UniProt_id==PDB2.id).group_by(Interactions.interactor_one, Interactions.interactor_two).all()
    
        # all_interacting_DIP format: [(u'1e9z', u'A', u'1e9z', u'A'), (u'2zl4', u'N', u'1klx', u'A'), ...]
        reversed_interactions_without_duplicates = create_reversed_interactions_removing_duplicates(interactions_DIP)
    
        p1 = aliased(PDB, name='p1')
        p2 = aliased(PDB, name='p2')
        i1 = aliased(Interacting_PDBs, name='i1')
        i2 = aliased(Interacting_PDBs, name='i2')
        # 3DID-interacting_PDB-chain_seq.sql
        #
        # SELECT p1.name, p1.chain, p2.name, p2.chain, i1.joined_interface_seq
        # FROM PDB as p1, Interacting_PDBs as i1, PDB as p2, Interacting_PDBs as i2
        # WHERE p1.id = i1.PDB_first_id
        # AND p2.id = i2.PDB_second_id
        # AND i1.id = i2.id;
    
        interactions_3DID = session_3DID.query(p1.name, p1.chain, p2.name, p2.chain, i1.joined_interface_seq).filter(p1.id==i1.PDB_first_id).filter(p2.id==i2.PDB_second_id).filter(i1.id==i2.id).all()
    
        if options.jena:
            interactions_JENA = open(options.jena)
    
            compare_interactions(dip_interactions_source=interactions_DIP, jena_interactions_source=interactions_JENA, \
                                    three_did_interactions_source=interactions_3DID, jena=True)
        else:
            # Compare 2 lists of interactions: DIP and 3DID, choose overlapping entires to build FASTA subsequently used by SVM
            compare_interactions(dip_interactions_source=interactions_DIP, three_did_interactions_source=interactions_3DID)

        # TODO THREE_DID_INTERACTIONS_HANDLER as a default this file might be used (if present on a package path,
        # optionally one might point one; if not present -- always calculate it)
    if options.most:
        # which_most = int(options.most)

        p1 = aliased(PDB, name='p1')
        p2 = aliased(PDB, name='p2')
        i1 = aliased(Interacting_PDBs, name='i1')
        i2 = aliased(Interacting_PDBs, name='i2')
        d1 = func.count(p1.domain_id).label('d1')
        d2 = func.count(p2.domain_id).label('d2')
        # 3DID-most_interact_domains.sql
        #
        # SELECT p1.domain_id, p2.domain_id, COUNT(p1.domain_id) AS d1, COUNT(p2.domain_id) AS d2
        # FROM PDB AS p1, Interacting_PDBs AS i1, PDB AS p2, Interacting_PDBs AS i2
        # WHERE p1.id = i1.PDB_first_id
        # AND p2.id = i2.PDB_second_id
        # AND i1.id = i2.id
        # GROUP BY p1.domain_id, p2.domain_id
        # HAVING d1 > 100 AND d2 > 100
        # ORDER BY d1, d2;
        
        most_interacting = session_3DID.query(p1.domain_id, p2.domain_id, d1, d2).filter(p1.id==i1.PDB_first_id).filter(p2.id== i2.PDB_second_id).filter(i1.id==i2.id).group_by(p1.domain_id, p2.domain_id).having(d1 > 100).having(d2 > 100).order_by(d1, d2).all()
        
        
        # most_interacting_domain_one = most_interacting[which_most][0]
        most_interacting_domain_one = most_interacting[-1][0]
        most_interacting_domain_two = most_interacting[-1][1]
        
        # SELECT p1.name, p1.chain, p2.name, p2.chain, i1.joined_interface_seq
        # FROM PDB AS p1, Interacting_PDBs AS i1, PDB AS p2, Interacting_PDBs AS i2
        # WHERE p1.id = i1.PDB_first_id
        # AND p2.id = i2.PDB_second_id
        # AND i1.id = i2.id
        # AND p1.domain_id=489 AND p2.domain_id=489;
        
        most_interacting_interfaces = session_3DID.query(p1.name, p1.chain, p2.name, p2.chain, i1.joined_interface_seq).filter(p1.id==i1.PDB_first_id).filter(p2.id==i2.PDB_second_id).filter(i1.id==i2.id).filter(p1.domain_id==most_interacting_domain_one).filter(p2.domain_id==most_interacting_domain_two).all()


        # Create FASTA file with interacting domain pairs interfaces sequence
        fasta_output = open('results/most_interacting_domain_pairs_interfaces.fa', 'w')

        for entry in most_interacting_interfaces:
            pdb_one = entry[0].strip()
            chain_one = entry[1].strip()
            pdb_two = entry[2].strip()
            chain_two = entry[3].strip()
            interface = entry[4].strip()

            to_write = '> %s%s - %s%s\n%s\n' % (pdb_one, chain_one, pdb_two, chain_two, interface)
            fasta_output.write(to_write)

        fasta_output.close()
        
        # Calculate identity % between 2 sequences

        from Bio import pairwise2

        alignments = pairwise2.align.globalxx("ACCGT", "ACG")
        # x No parameters.  Identical characters have score of 1, otherwise 0.
        # x No gap penalties.
        # http://www.biopython.org/DIST/docs/api/Bio.pairwise2-module.html

        identity = (alignments[0][2] / (alignments[0][4]+1))*100

if __name__ == '__main__':
    main()
