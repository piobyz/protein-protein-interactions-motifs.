#!/usr/bin/env python
# encoding: utf-8
"""
Transfer PDB info about a particular protein based on its UniProt id.
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


from Bio import SeqIO
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from DBDIP import Interactors, Interactions, Structures, PDB_UniProt


def main():
        # Retrieve all proteins from Interactors Table, get their UniProt ids
        # and retireve corresponding PDB name+chain from PDB_UniProt mapping Table.
        # Finally, store relations in a Structures Table.
        query = session.query(Interactors).order_by(Interactors.id)
        all_interactors = query.all()
        for interactor in all_interactors:
            pdb_list = session.query(PDB_UniProt).filter(PDB_UniProt.uniprot==interactor.uniprot_id).all()
            if pdb_list:
                for pdb_item in pdb_list:
                    interactor.structures_entry.append(pdb_item)
                    session.commit()

if __name__ == '__main__':
    meta = MetaData()
    Base = declarative_base(metadata=meta)
    
    # Database with Interactors and Interactions
    engine = create_engine('sqlite:///DIP-Hpylo.db', echo=False)
    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    main()
