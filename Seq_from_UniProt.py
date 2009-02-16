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

from Bio import SeqIO
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import relation, backref, join, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.exc import IntegrityError

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///UniProt_Seq.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
Base = declarative_base(metadata=meta)


class UniProtSeq(Base):
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

meta.create_all(engine)

if __name__ == '__main__':
    # !!! RUN ONCE ONLY !!!
    # mapping_file = open('../uniprot_sprot.fasta')
    # 
    # for cur_record in SeqIO.parse(mapping_file, "fasta"):
    #     title = str(cur_record.name).split('|')[1]
    #     seq = cur_record.seq.tostring()
    # 
    #     try:
    #         new_UniProtSeq = UniProtSeq(uniprot=title, sequence=seq)
    #         session.add(new_UniProtSeq)
    #         session.commit()
    #     except IntegrityError:
    #         session.rollback()
    #         print 'Entry: %s already exist in the UniProtSeq' % new_UniProtSeq

    query = session.query(UniProtSeq.uniprot, UniProtSeq.sequence).filter(UniProtSeq.uniprot=='P18646')
    print query.first()
