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


from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import relation, backref, join, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from Seq_from_UniProt import UniProtSeq

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///DB/Mmusc20090126.db', echo=True)
# Session = sessionmaker(bind=engine)
# session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)

# engine_uniprot = create_engine('sqlite:///UniProt_Seq.db', echo=False)
# Session_uniprot = sessionmaker(bind=engine_uniprot)
# session_uniprot = Session_uniprot()

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


meta.create_all(engine)

if __name__ == '__main__':
    # try:
    #     new_PDB = PDB(name='1aa2', chain='D', sequence='ACCACATTTGGGTCTGA')
    #     session.add(new_PDB)
    #     session.commit()
    # except IntegrityError:
    #     session.rollback()
    #     print 'PDB entry: %s already exist in the DB' % new_PDB
    
    # try:
    #     new_interactor = Interactors(id='44593', dip_id='DIP-44593N', uniprot_id='Q9WVG6',
    #         pdb_id='2342')
    #     session.add(new_interactor)
    #     session.commit()
    # except IntegrityError:
    #     session.rollback()
    #     print 'Interactors entry: %s already exist in the DB' % new_interactor
    # 
    # try:
    #     new_interaction = Interactions('13', 'DIP-13E', '951', '278')
    #     session.add(new_interaction)
    #     session.commit()
    # except IntegrityError:
    #     session.rollback()
    #     print 'Interactions entry: %s already exist in the DB' % new_interaction
    
    
    # query = session.query(PDB.name, PDB.chain).order_by(PDB.id)
    # print query.first()
    
    # query = session.query(Interactors.id, Interactors.dip_id).order_by(Interactors.id)
    # print query.first()
    # 
    # query = session.query(Interactions.id, Interactions.dip_id).order_by(Interactions.id)
    # print query.first()
    
    ################ PDB_UniProt TABLE ################
    # !!!Run only once to feed the database!!!
    # mapping_file = open('../pdbsws_chain.txt')
    # 
    # for line in mapping_file:
    #     arguments = line.split(' ')
    #     try:
    #         new_PDB_UniProt = PDB_UniProt(pdb=arguments[0], chain=arguments[1], uniprot=(arguments[2]).strip())
    #         session.add(new_PDB_UniProt)
    #         session.commit()
    #     except IntegrityError:
    #         session.rollback()
    #         print 'Entry: %s already exist in the DB' % new_PDB_UniProt

    ################ PDB_UniProt.sequence TABLE ################
    # !!! Run only once !!!
    # It transfers sequences obtained from UniProt (uniprot_sprot.fasta) on 15.02.2009
    # from 
    # WARNING: Not all sequences are present in this file.

    # all_structures = session.query(Structures).all()
    # for structure in all_structures:
    #     pdb_entry = session.query(PDB_UniProt).filter(PDB_UniProt.id==structure.PDB_UniProt_id).one()
    #     try:
    #         uniprot_seq = session_uniprot.query(UniProtSeq.sequence).filter(UniProtSeq.uniprot==pdb_entry.uniprot).one()
    #         pdb_entry.sequence = uniprot_seq[0]
    #         session.flush()
    #         session.commit()
    #     except NoResultFound:
    #         print 'No results for: %s' % pdb_entry.uniprot

    query = session.query(PDB_UniProt.uniprot).order_by(PDB_UniProt.id)
    print query.first()
