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

engine = create_engine('sqlite:///:memory:', echo=False)
# engine = create_engine('sqlite:///DIP.db')
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)


class PDB(Base):
    __tablename__ = 'PDB'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    sequence = Column(String, nullable=False)

    __table_args__  = (UniqueConstraint('name', 'chain'), {})

    def __init__(self, **kw):
        self.update(**kw)

    def update(self, **kw):
        if 'name' in kw:
            self.name = kw['name']
        if 'chain' in kw:
            self.chain = kw['chain']
        if 'sequence' in kw:
            self.sequence = kw['sequence']

    def __repr__(self):
        return "<PDB('%s', '%s')>" % (self.name, self.chain)


class Interactors(Base):
    __tablename__ = 'Interactors'

    id = Column(Integer, primary_key=True, index=True)
    dip_id = Column(String, nullable=False, unique=True, index=True)
    uniprot_id = Column(String, nullable=False, unique=True, index=True)
    pdb_id = Column(Integer, ForeignKey('PDB.id'), index=True)

    # many-to-one Interactors * 1 PDB
    pdb_entry = relation('PDB', backref=backref('Interactors'))

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

meta.create_all(engine)

if __name__ == '__main__':
    try:
        new_PDB = PDB(name='1aa2', chain='D', sequence='ACCACATTTGGGTCTGA')
        session.add(new_PDB)
        session.commit()
    except IntegrityError:
        session.rollback()
        print 'PDB entry: %s already exist in the DB' % new_PDB

    try:
        new_interactor = Interactors(id='44593', dip_id='DIP-44593N', uniprot_id='Q9WVG6',
            pdb_id='2342')
        session.add(new_interactor)
        session.commit()
    except IntegrityError:
        session.rollback()
        print 'Interactors entry: %s already exist in the DB' % new_interactor

    try:
        new_interaction = Interactions('13', 'DIP-13E', '951', '278')
        session.add(new_interaction)
        session.commit()
    except IntegrityError:
        session.rollback()
        print 'Interactions entry: %s already exist in the DB' % new_interaction


    query = session.query(PDB.name, PDB.chain).order_by(PDB.id)
    print query.first()

    query = session.query(Interactors.id, Interactors.dip_id).order_by(Interactors.id)
    print query.first()

    query = session.query(Interactions.id, Interactions.dip_id).order_by(Interactions.id)
    print query.first()
