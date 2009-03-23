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
__status__ = "Alpha"


import sys
import os
import os.path # os.path.basename, os.path.exists

from optparse import OptionParser

import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, join, sessionmaker

import DB_DIP
import DB_3DID
import misc

# Logging configuration
logging.config.fileConfig("log/logging.conf")
log_load = logging.getLogger('load')


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
# TODO create dir external_files/ for those? It should be possible to specify path to those file
in options

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
    parser.add_option("-d", "--3did", action="store_true", dest="did", metavar="FILE", help="Parse 3DID flat FILE. [default: %default]")
    parser.add_option("-c", "--compare", action="store_true", dest="compare", default=False, help="Compare set of PDBs from single species between DIP, 3DID and JENA. [default: %default]")
    parser.add_option("-j", "--jena", dest="jena", default=None, metavar="FILE", help="Provide path to the JENA dataset. [default: %default]")
    parser.add_option("-l", "--clean", action="store_true", dest="clean", default=False, help="Clean all temp files unless something gone wrong. [default: %default]")
    parser.add_option("-m", "--most", dest="most", help="Prepare fasta file for the most interacting pair of domains from 3DID. Specify which pair should it be (1st, 2nd, ... most). [default: %default]")
    # TODO Implement clean.

    (options, args) = parser.parse_args()
    if(len(args) == 0 and not options.uniseq and not options.uniprot and not options.did and not options.compare):
        parser.print_help()
        sys.exit(1)

    log_load.debug('Module has been called by: %s %s' % (options, args))
    
    # TODO Check dependencies: which tasks can be run when, e.g. uniprot and uniseq can be run when
    #       at the same time arg is provided (and new DIP DB created) OR when DIP DB is provided
    #       maybe not the best example... but think about scenarios like this

    if len(args)==1:
        try:
            input_file = open(args[0])
        except IOError:
            log_load.exception('There is no such file: %s' % options.input)
            sys.exit(1)
    
        file_name = os.path.basename(args[0]).split('.')[0]
        
        # Get the DB session (run meta.create_all(engine) and return session)
        session_DIP = DB_DIP.get_session(file_name, options.echo, options.test)
        
        # This means user has a *.mif25 file and we should parse it and store in DB
        # SAX parsing DIP's *.mif25 file and putting it in <species date>.db
        DB_DIP.sax_parse(input_file, session_DIP)
    
    if options.uniprot or options.uniseq:
        # session_DIP = DB_DIP.get_session(file_name, options.echo, options.test)

        if options.uniprot:
            # Create PDB_UniProt with mappings between each PDB+chain and UniProt
            DB_DIP.pdb2uniprot(session_DIP)
            log_load.debug('PDB to UniProt mapping DB has been created.')
        if options.uniseq:
            # Feed the PDB_UniProt TABLE with sequences for each UniProt
            # FIXME Not sure if this should be a sepate step OR *always* connected with the one above
            # and this file is common to all *.mif25 so there is no need to generate more than 1!!
            DB_DIP.uniprot_sequence(session_DIP)
            log_load.debug('Sequence for each UniProt has been transfered.')
    else:
        log_load.debug('PDB to UniProt mapping has NOT been applied in this run.')
    
    if options.did or options.compare or options.most:
        session_3DID = DB_3DID.get_session(options.echo, options.test)

        if options.did:
            # Creates DB with 3DID interactions (schema: doc/3DID_schema.pdf)
            # TODO check if that DB already exist, if yes -- skip this step
            try:
                DB_3DID.parse_3did(options.did, session_3DID)
                log_load.debug('3DID flat file has been parsed and data inserted into DB.')
            except IOError, e:
                log_load.exception('Unable to open file: %s' % options.did)
        else:
            log_load.debug('3DID data has not been created/updated due to options set.')
    
        if options.compare:
            interactions_DIP = DB_DIP.both_interacting_from_DIP(session_DIP)
    
            # all_interacting_DIP format: [(u'1e9z', u'A', u'1e9z', u'A'), (u'2zl4', u'N', u'1klx', u'A'), ...]
            reversed_interactions_without_duplicates = DB_DIP.create_reversed_interactions_removing_duplicates(interactions_DIP)
    
            interactions_3DID = DB_3DID.both_interacting_from_3DID(session_3DID)

            if options.jena:
                try:
                    interactions_JENA = open(options.jena)
                except IOError:
                    log_load.exception('File not found: %s' % options.jena)
                    # TODO Should stop 'compare routine' at this point ?
                    # TODO Provide info (and files themselfs) where JENA files are located
    
                misc.compare_interactions(dip_interactions_source=interactions_DIP, jena_interactions_source=interactions_JENA, \
                                        three_did_interactions_source=interactions_3DID, jena=True)
            else:
                # Compare 2 lists of interactions: DIP and 3DID, choose overlapping entries to create FASTA file used by SVM later
                misc.compare_interactions(dip_interactions_source=interactions_DIP, three_did_interactions_source=interactions_3DID)

        if options.most:
            try:
                which_most = int(options.most)
            except ValueError:
                log_load.exception('Wrong value for the NUMBER of the most interacting pair of domains: %s' % options.most)

            most_interacting_domains_3DID = DB_3DID.most_interacting_domains_from_3DID(session_3DID)
        
            # Choose subset of the "which_most"-most interacting pair of domains
            most_interacting_domain_one = most_interacting_domains_3DID[-which_most][0]
            most_interacting_domain_two = most_interacting_domains_3DID[-which_most][1]
        
            most_interacting_interfaces = most_interacting_interfaces_from_3DID(session_3DID,\
                    most_interacting_domain_one, most_interacting_domain_two)

            misc.output_fasta_file(most_interacting_interfaces)
        
            misc.calculate_identity()

        
if __name__ == '__main__':
    main()
    log_load.info('END OF SCRIPT.')