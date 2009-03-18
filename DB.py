#!/usr/bin/env python
# encoding: utf-8
"""
SQLAlchemy mappers for PPIMotifs module.
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

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///PPI-1a.db')
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)


homologues = Table('Homologues', meta,
    Column('protein_seed_id', Integer, ForeignKey('Proteins_seed.id')),
    Column('protein_putative_id', Integer, ForeignKey('Proteins_putative.id')))


class PDB(Base):
    __tablename__ = 'PDB'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    __table_args__ = (UniqueConstraint('name', 'chain'), {})

    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        if 'name' in kw:
            self.name = kw['name']
        if 'chain' in kw:
            self.chain = kw['chain']

    def __repr__(self):
        return "<PDB('%s', '%s')>" % (self.name, self.chain)


class Protein_seed(Base):
    __tablename__ = 'Proteins_seed'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sequence = Column(String, nullable=False, unique=True, index=True)
    length = Column(Integer, nullable=False)
    alignment = Column(String, nullable=False)
    pdb_id = Column(Integer, ForeignKey('PDB.id'), index=True)

    # many-to-one Protein_seed * 1 PDB
    pdb_entry = relation('PDB', backref=backref('Proteins_seed'))

    # many-to-many Protein_seed * * Protein_putative
    homologues_entry = relation('Protein_putative', secondary=homologues)

    def __init__(self, name, sequence, length, alignment, pdb_id):
        self.name = name
        self.sequence = sequence
        self.length = length
        self.alignment = alignment
        self.pdb_id = pdb_id

    def __repr__(self):
        return "<Protein_seed('%s', '%s', '%s', '%s')>" % (self.name, self.sequence,
            self.length, self.alignment)


class Patch_seed(Base):
    __tablename__ = 'Patches_seed'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sequence = Column(String, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    alignment = Column(String, nullable=False)
    protein_seed_id = Column(Integer, ForeignKey('Proteins_seed.id'), index=True)

    # many-to-one Patch_seed * 1 Protein_seed
    protein_seed_entry = relation('Protein_seed', backref=backref('Patches_seed'))

    def __init__(self, protein_seed_id, name, sequence, length, alignment):
        self.protein_seed_id = protein_seed_id
        self.name = name
        self.sequence = sequence
        self.length = length
        self.alignment = alignment

    def __repr__(self):
        return "<Patch_seed('%s')>" % (self.name)


class Protein_putative(Base):
    __tablename__ = 'Proteins_putative'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    primary_accession_number = Column(String, nullable=False, index=True)
    description = Column(String)
    sequence = Column(String, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    alignment = Column(String, nullable=False)

    def __init__(self, name, primary_accession_number, description, sequence, length, alignment):
        self.name = name
        self.primary_accession_number = primary_accession_number
        self.description = description
        self.sequence = sequence
        self.length = length
        self.alignment = alignment

    def __repr__(self):
        return "<Protein_putative('%s', '%s')>" % (self.name, self.primary_accession_number)


class Patch_putative(Base):
    __tablename__ = 'Patches_putative'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sequence = Column(String, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    alignment = Column(String, nullable=False)
    protein_putative_id = Column(Integer, ForeignKey('Proteins_putative.id'), index=True)

    # many-to-one Patch_putative * 1 Protein_putative
    protein_putative_entry = relation('Protein_putative', backref=backref('Patches_putative'))

    def __init__(self, protein_putative_id, name, sequence, length, alignment):
        self.protein_putative_id = protein_putative_id
        self.name = name
        self.sequence = sequence
        self.length = length
        self.alignment = alignment

    def __repr__(self):
        return "<Patch_putative('%s')>" % (self.name)


class Interaction(Base):
    __tablename__ = 'Interactions'

    first_protein_putative_id = Column(Integer, ForeignKey('Proteins_putative.id'),
        primary_key=True, index=True)
    second_protein_putative_id = Column(Integer, ForeignKey('Proteins_putative.id'),
        primary_key=True, index=True)
    seed_reaction = Column(String, nullable=False, index=True)

    # many_to_many Protein_putative * * Protein_putative
    corresponding_putative_entry = relation('Protein_putative', backref='Interactions',
        primaryjoin=first_protein_putative_id==Protein_putative.id)

    def __init__(self, first_protein_putative_id, second_protein_putative_id, seed_reaction):
        self.first_protein_putative_id = first_protein_putative_id
        self.second_protein_putative_id = second_protein_putative_id
        self.seed_reaction = seed_reaction

    def __repr__(self):
        return "<Interaction(%s %s '%s')>" % (self.first_protein_putative_id,
            self.second_protein_putative_id, self.seed_reaction)


meta.create_all(engine)

if __name__ == '__main__':
    new_PDB = PDB(name='1aa2', chain='D')
    session.add(new_PDB)

    new_PDB = PDB(name='1aa2', chain='A')
    session.add(new_PDB)

    session.commit()

    try:
        new_PDB = PDB(name='1aa2', chain='D')
        session.add(new_PDB)
        session.commit()
    except IntegrityError:
        session.rollback()
        print 'PDB entry: %s already exist in the DB' % new_PDB

    new_protein = Protein_seed('1st protein', 'DSGFFGHFGJ', 13, 'SDF-DFGDFG---FG', 1)
    session.add(new_protein)
    session.commit()

    query = session.query(PDB.name, PDB.chain).order_by(PDB.id)
    print query.all()

    # distinct_seg.sql
    # 
    # SELECT COUNT(DISTINCT Patches_seed.sequence)
    # FROM Patches_seed, Proteins_seed, Homologues, Proteins_putative, Interactions
    # WHERE (Patches_seed.length>2)
    # AND (Proteins_seed.name=Interactions.seed_reaction)
    # AND (
    #     (Proteins_seed.id=Homologues.protein_seed_id)
    #     AND (Homologues.protein_putative_id=Proteins_putative.id)
    # )
    # AND (
    #     (Proteins_putative.name=Interactions.first_protein_putative_id)
    #     OR (Proteins_putative.name=Interactions.second_protein_putative_id)
    # );



