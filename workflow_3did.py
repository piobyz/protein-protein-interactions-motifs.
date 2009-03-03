#!/usr/bin/env python
# encoding: utf-8
"""
Protein-protein interactions motifs.
Module for classifying putative PPI using String Kernels and Support Vector Machines (SVM).
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import os
from Bio import SeqIO
from DB_3did_parser import Domain, Interaction, PDB, Interacting_PDBs, Interface
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError


def main():
    interfaces = session.query(Interacting_PDBs.joined_interface_seq).all()
    sample_interfaces = interfaces[1000:2000]
    
    sample_fasta_handler = open('PPI-3did-onethousand.fa', 'a')
    
    for interface in sample_interfaces:
        sample_fasta_handler.write('> XXX\n')
        sample_fasta_handler.write('%s\n' % interface)

    sample_fasta_handler.close()

if __name__ == '__main__':
    meta = MetaData()
    Base = declarative_base(metadata=meta)

    engine = create_engine('sqlite:///../DB/3did.db', echo=False)
    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    main()
