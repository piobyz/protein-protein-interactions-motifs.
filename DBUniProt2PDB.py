#!/usr/bin/env python
"""
SQLAlchemy mappers for PDB_UniProt module.
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
engine = create_engine('sqlite:///PDB_UniProt.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)


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
    
    mapping_file = open('../pdbsws_chain.txt')
    
    for line in mapping_file:
        arguments = line.split(' ')
        try:
            new_PDB_UniProt = PDB_UniProt(pdb=arguments[0], chain=arguments[1], uniprot=(arguments[2]).strip())
            session.add(new_PDB_UniProt)
            session.commit()
        except IntegrityError:
            session.rollback()
            print 'Entry: %s already exist in the DB' % new_PDB_UniProt

    # query = session.query(PDB_UniProt.pdb, PDB_UniProt.chain, PDB_UniProt.uniprot).order_by(PDB_UniProt.id)
    # print query.first()
