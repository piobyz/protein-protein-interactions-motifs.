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
from DB import Protein_seed, PDB, Patch_seed, Protein_putative, Patch_putative, Interaction
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError


def main():

    input_files = os.listdir('../alignments')
    
    for single_file in input_files:
        input_file = open('../alignments' + os.sep + single_file)
    
        # each file should have an alignment of exactly 4 sequences:
        # seed entry, its patch, homologous protein, its patch
        # cycle to recognize them and retrieve its different features
        cycle = 1
    
        for cur_record in SeqIO.parse(input_file, "fasta"):
            records = []
    
            title = str(cur_record.name)
            description = str(cur_record.description)
            aligned_seq = cur_record.seq
    
            ######## TABLE Proteins_seed ########
            if cycle == 1:
                ######## TABLE PDB ########
                try:
                    pdb_id = title.split('/')[2][3:-1]
                    pdb_chain = title.split('/')[2][-1]
                    # FIXME what if there will be no chain indicator?
                    try:
                        new_pdb = PDB(name=pdb_id, chain=pdb_chain)
                        session.add(new_pdb)
                        session.flush()
                        pdb_last_id = new_pdb.id
                    except IntegrityError:
                        session.rollback()
                        # If pair (pdb_id+chain) already exist, retrieve its PDB.id
                        query = session.query(PDB.id).filter(PDB.name==pdb_id).filter(PDB.chain==pdb_chain)
                        try:
                            pdb_last_id = query.one()[0]
                        except Exception, e:
                            print 'Two identical PDB entries??'
                except IndexError:
                    print "Uncorrect FASTA file (does not have a correct description)."
                try:
                    name = title.split('/')[1]
                except IndexError:
                    print "Uncorrect FASTA file (does not have a correct description)."
    
                sequence = ''.join(filter(lambda s: s != '-', aligned_seq.tomutable()))
                sequence_length = len(sequence)
                alignment = aligned_seq.tostring()
                try:
                    new_protein_seed = Protein_seed(name, sequence, sequence_length, alignment,
                    pdb_last_id)
                    session.add(new_protein_seed)
                    session.flush()
                    protein_seed_last_id = new_protein_seed.id
                except IntegrityError:
                    session.rollback()
                    # If sequence of seed protein already exist, retrieve its Proteins_seed.id
                    query = session.query(Protein_seed.id).filter(Protein_seed.sequence==sequence)
                    try:
                        protein_seed_last_id = query.one()[0]
                    except Exception, e:
                        print 'Two identical Protein_seed.sequence entries??'
    
            ######## TABLE Patches_seed ########
            elif cycle == 2:
                name = ':'.join(title.split(':')[:-1])
                alignment = aligned_seq.tostring()
    
                # we take every contiguous sequence as patch
                patches = filter(lambda s: s != '', aligned_seq.tostring().split('-'))
                for patch in patches:
                    patch_length = len(patch)
    
                    new_seed_patch = Patch_seed(protein_seed_last_id, name, patch, patch_length,
                        alignment)
                    session.add(new_seed_patch)
                    session.flush()
    
            ######## TABLE Proteins_putative ########
            elif cycle == 3:
                try:
                    name = title.split('|')[2]
                    primary_accession_number = title.split('|')[1]
                except IndexError:
                    print "Uncorrect FASTA file (does not have a correct description)."
    
                sequence = ''.join(filter(lambda s: s != '-', aligned_seq.tomutable()))
                sequence_length = len(sequence)
                alignment = aligned_seq.tostring()
    
                new_protein_putative = Protein_putative(name, primary_accession_number,
                    description, sequence, sequence_length, alignment)
                session.add(new_protein_putative)
                ######## TABLE Homologues ########
                # Add association to homologues table
                new_protein_seed.homologues_entry.append(new_protein_putative)
    
                session.flush()
                protein_putative_last_id = new_protein_putative.id
    
            ######## TABLE Patches_putative ########
            elif cycle == 4:
                name = ':'.join(title.split(':')[:-1])
                alignment = aligned_seq.tostring()
    
                # we take every contiguous sequence as patch
                patches = filter(lambda s: s != '', aligned_seq.tostring().split('-'))
                for patch in patches:
                    patch_length = len(patch)
    
                    new_putative_patch = Patch_putative(protein_putative_last_id, name, patch,
                        patch_length, alignment)
                    session.add(new_putative_patch)
                    session.flush()
    
            ### end of cases
            session.commit()
            cycle += 1

    ######## TABLE Interactions ########
    interactions_file = open('../DB_interactions/I1_total.db')

    for line in interactions_file:
        first_inter_protein = (line.split('\t')[2]).split(':')[0]
        second_inter_protein = (line.split('\t')[2]).split(':')[1]
        seed_reaction_list = (line.split('\t')[-1]).split(',')

        # FIXME find 1st entry with interacting name
        # Should be only one, make this entries unique in 'Proteins_putative' table
        # [05.02.2009] Hmmmm?
        query = session.query(Protein_putative.id).filter(Protein_putative.name
            == first_inter_protein).order_by(Protein_putative.id)
        if query.first():
            first_inter_protein_id = query.first()[0]

        query = session.query(Protein_putative.id).filter(Protein_putative.name
            == second_inter_protein).order_by(Protein_putative.id)
        if query.first():
            second_inter_protein_id = query.first()[0]

        for single_seed_reaction in seed_reaction_list:
            try:
                new_interaction = Interaction(first_inter_protein_id, second_inter_protein_id,
                    single_seed_reaction.strip())
                session.add(new_interaction)
            except UnboundLocalError:
                pass
            try:
                session.flush()
                session.commit()
            except IntegrityError:
                session.rollback()

if __name__ == '__main__':
    meta = MetaData()
    Base = declarative_base(metadata=meta)

    engine = create_engine('sqlite:///PPI-1a.db', echo=True)
    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    main()
