#!/usr/bin/env python
"""
Parser for 3DID flat file connected with mapper to SQLAlchemy classes.
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"

# TODO Remove redundancy in Domains and PDB(PDB-if they are really the same, not only name+chain, ->sequence!)


from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import relation, backref, join, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.exc import IntegrityError

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///../DB/3did_test.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)


class Domain(Base):
    __tablename__ = 'Domains'

    id = Column(Integer, primary_key=True, index=True)
    PfamA = Column(String, nullable=False, index=True)
    PfamB = Column(String, nullable=False, index=True)
    family_version = Column(String, nullable=False, index=True)
    __table_args__  = (UniqueConstraint('PfamA', 'PfamB', 'family_version'), {})

    def __init__(self, PfamA, PfamB, family_version):
        self.PfamA = PfamA
        self.PfamB = PfamB
        self.family_version = family_version

    def __repr__(self):
        return "<Domain('%s.%s')>" % (self.PfamB, self.family_version)


class Interaction(Base):
    __tablename__ = 'Interactions'

    first_domain_id = Column(Integer, ForeignKey('Domains.id'),
        primary_key=True, index=True)
    second_domain_id = Column(Integer, ForeignKey('Domains.id'),
        primary_key=True, index=True)

    # many_to_many Domains * * Domains
    interacting_domains = relation('Domain', backref='Interactions',
        primaryjoin=first_domain_id==Domain.id)

    def __init__(self, first_domain, second_domain):
        self.first_domain_id = first_domain
        self.second_domain_id = second_domain

    def __repr__(self):
        return "<Interaction(%s | %s)>" % (self.first_domain, self.second_domain)


class PDB(Base):
    __tablename__ = 'PDB'

    id = Column(Integer, primary_key=True, index=True)
    # domain_id = Column(Integer, ForeignKey('Domains.id'), primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    seqRes_range = Column(String, nullable=False)
    seq_length = Column(Integer, nullable=False)
    sequence = Column(String, nullable=False, index=True)
    
    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        # if 'domain_id' in kw:
        #     self.domain_id = kw['domain_id']
        if 'name' in kw:
            self.name = kw['name']
        if 'chain' in kw:
            self.chain = kw['chain']
        if 'seqRes_range' in kw:
            self.seqRes_range = kw['seqRes_range']
        if 'seq_length' in kw:
            self.seq_length = kw['seq_length']
        if 'sequence' in kw:
            self.sequence = kw['sequence']

    def __repr__(self):
        return "<PDB('%s|%s')>" % (self.name, self.chain)


class Interacting_PDBs(Base):
    __tablename__ = 'Interacting_PDBs'

    PDB_first_id = Column(Integer, ForeignKey('PDB.id'), primary_key=True, index=True)
    PDB_second_id = Column(Integer, ForeignKey('PDB.id'), primary_key=True, index=True)
    joined_interface_seq = Column(String, nullable=False, index=True)
    joined_interface_len = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    Zscore = Column(Integer, nullable=False)

    # many_to_many PDB * * PDB
    interacting_interfaces = relation('PDB', backref='Interacting_PDBs',
        primaryjoin=PDB_first_id==PDB.id)

    def __init__(self, PDB_first_id, PDB_second_id, joined_interface_seq, joined_interface, score, Zscore):
        self.PDB_first_id = PDB_first_id
        self.PDB_second_id = PDB_second_id
        self.joined_interface_seq = joined_interface_seq
        self.joined_interface_len = joined_interface_len
        self.score = score
        self.Zscore = Zscore

    def __repr__(self):
        return "<Interacting_PDBs('%s|%s')>" % (self.PDB_first_id, self.PDB_second_id)


class Interface(Base):
    __tablename__ = 'Interface'

    id = Column(Integer, primary_key=True, index=True)
    corresponding_PDB_id = Column(Integer, index=True)
    residue_first = Column(String, nullable=False, index=True)
    seqRes_first = Column(Integer, nullable=False)
    residue_second = Column(String, nullable=False, index=True)
    seqRes_second = Column(Integer, nullable=False)
    contact_type = Column(String, nullable=False, index=True)

    def __init__(self, corresponding_PDB_id, residue_first, seqRes_first, residue_second, seqRes_second, contact_type):
        self.corresponding_PDB_id = corresponding_PDB_id
        self.residue_first = residue_first
        self.seqRes_first = seqRes_first
        self.residue_second = residue_second
        self.seqRes_second = seqRes_second
        self.contact_type = contact_type

    def __repr__(self):
        return "<Interface('%s: %s|%s')>" % (self.corresponding_PDB_id, self.residue_first, self.residue_second)


meta.create_all(engine)

if __name__ == '__main__':
    # !!! RUN ONCE ONLY !!!
    threedid_file = open('../3did_flat_Feb_15_2009.dat')
    
    for line in threedid_file:
        if line.startswith('#=ID'):
            pfams = line.split('\t')

            first_pfamA = pfams[1].strip()
            second_pfamA = pfams[2].strip()

            first_pfamB = pfams[3].strip().lstrip('(').rstrip('@Pfam').split('.')[0]
            first_family_version = pfams[3].strip().lstrip('(').rstrip('@Pfam').split('.')[1]
            second_pfamB = pfams[4].strip().rstrip('@Pfam)').split('.')[0]
            second_family_version = pfams[4].strip().rstrip('@Pfam)').split('.')[1]

            ######## TABLE Domains ########
            try:
                first_domain = Domain(first_pfamA, first_pfamB, first_family_version)
                session.add(first_domain)
                session.flush()
                first_domain_last_id = first_domain.id
            except IntegrityError:
                session.rollback()
                # If pair (PfamA+PfamB) already exist, retrieve its Domains.id
                try:
                    first_domain_last_id = session.query(Domain.id).filter(Domain.PfamA==first_pfamA).filter(Domain.PfamB==first_pfamB).filter(Domain.family_version==first_family_version).one()[0]
                    print first_domain_last_id
                except Exception, e:
                    print 'Two identical Domain entries??'
            try:
                second_domain = Domain(second_pfamA, second_pfamB, second_family_version)
                session.add(second_domain)
                session.flush()
                second_domain_last_id = second_domain.id
            except IntegrityError:
                session.rollback()
                # If pair (pdb_id+chain) already exist, retrieve its PDB.id
                try:
                    second_domain_last_id = session.query(Domain.id).filter(Domain.PfamA==second_pfamA).filter(Domain.PfamB==second_pfamB).filter(Domain.family_version==second_family_version).one()[0]
                    print second_domain_last_id
                except Exception, e:
                    print 'Two identical Domain entries??'
            session.commit()
            
            ######## TABLE Interactions ########
            try:
                new_interaction = Interaction(first_domain_last_id, second_domain_last_id)
                session.add(new_interaction)
                session.flush()
            except UnboundLocalError:
                pass
            session.commit()
            # print first_pfamA, second_pfamA, first_pfamB, second_pfamB
        elif line.startswith('#=3D'):
            chains = line.split('\t')

            pdb_name = chains[1]

            first_chain = chains[2].split(':')[0]
            first_chain_range = chains[2].split(':')[1]

            second_chain = chains[3].split(':')[0]
            second_chain_range = chains[3].split(':')[1]

            # First loop will be empty, but for each next run it will contain a whole sequence for each interface
            try:
                if first_interface_seq and second_interface_seq:
                    first_seq = ''.join(first_interface_seq)
                    first_seq_len = len(first_interface_seq)
                    second_seq = ''.join(second_interface_seq)
                    second_seq_len = len(second_interface_seq)
                    joined_interface_seq = ''.join(first_interface_seq) + ''.join(second_interface_seq)
                    joined_interface_len = len(joined_interface_seq)
                    
                    ######## TABLE PDB ########
                    try:
                        first_pdb = PDB(name=pdb_name, chain=first_chain, seqRes_range=first_chain_range, sequence=first_seq, seq_length=first_seq_len)
                        # FIXME Add domain_id information
                        session.add(first_pdb)
                        session.flush()
                        first_pdb_last_id = first_pdb.id
                    except IntegrityError:
                        session.rollback()

                    try:
                        second_pdb = PDB(name=pdb_name, chain=second_chain, seqRes_range=second_chain_range, sequence=second_seq, seq_length=second_seq_len)
                        # FIXME Add domain_id information
                        session.add(second_pdb)
                        session.flush()
                        second_pdb_last_id = second_pdb.id
                    except IntegrityError:
                        session.rollback()

                    score = chains[4].strip()
                    Zscore = chains[5].strip()

                    ######## TABLE Interacting_PDBs ########
                    try:
                        interacting_pdbs = Interacting_PDBs(first_pdb_last_id, second_pdb_last_id, joined_interface_seq, joined_interface_len, score, Zscore)
                        session.add(interacting_pdbs)
                        session.flush()
                    except IntegrityError:
                        session.rollback()
            except NameError, e:
                # FIXME create instance of PDB here, but w/o first_seq and first_seq_len (the same with second)
                # and then update this instance with those 2 attributes
                print "Most probably it's 1st run, so there is no interface to insert yet.", e
            session.commit()

            # Init sequence tables for the1st sequence and then empty each after each #=3D line
            # FIXME This way, the last interface won't be INSERTed!!!
            first_interface_seq = []
            second_interface_seq = []

            # print pdb_name, first_chain, first_chain_range, second_chain, second_chain_range, score, Zscore
        elif not line.startswith('//'):
            contact_residues = line.split('\t')

            first_interface_residue = contact_residues[0].strip()
            first_interface_residue_position = contact_residues[2].strip()

            second_interface_residue = contact_residues[1].strip()
            second_interface_residue_position = contact_residues[3].strip()

            contact_type = contact_residues[4].strip()

            first_interface_seq.append(first_interface_residue)
            second_interface_seq.append(second_interface_residue)

            ######## TABLE Interface ########
            try:
                new_interface = Interface(first_pdb_last_id, first_interface_residue, first_interface_residue_position,
                second_interface_residue, second_interface_residue_position, contact_type)
                session.add(new_interface)
                session.flush()
            except IntegrityError:
                session.rollback()
            except NameError:
                pass

            # print first_interface_residue, first_interface_residue_position, second_interface_residue, second_interface_residue_position, contact_type
            session.commit()

        elif line.startswith('//'):
            pass
