#!/usr/bin/env python
# encoding: utf-8
"""
Miscellaneous tools for :mod:`PPIM` package: :func:`get_pdbid_chain`, :func:`find_overlaps`,
:func:`compare_interactions`, :func:`output_fasta_file`.
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "..."
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Alpha"

import os
import logging
import logging.config

import random # random.choice in output_fasta_file()

# Logging configuration
logging.config.fileConfig("/Users/piotr/Projects/Thesis/Spring/PPIM/log/logging.conf")
log_load = logging.getLogger('load')
log_results = logging.getLogger('results')


def get_pdbid_chain(source, kind=None, chain=False):
    """Returns dictionary with interactions. Depending on *chain* value, key is PDB id or
    two PDBs and its chains, value is empty string or interface sequence.
    
    * **source** 5-element list with PDBs and chains and interface sequence.
    * **kind** one-word description of where interactions come from (DIP, 3DID, JENA, etc.).
    * **chain** if True, chains corresponding to PDBs are returned too.

    >>> get_pdbid_chain([(u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'1n8j', u'F', u'DDDDDRKKRKWDKDDD'), (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'), (u'1n8j', u'I', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD'), (u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD')], kind='DIP')
    {u'1n8j': '', u'aa8j': '', u'1ssj': ''}

    >>> get_pdbid_chain([(u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'1n8j', u'F', u'DDDDDRKKRKWDKDDD'), (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'), (u'1n8j', u'I', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD'), (u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD')], kind='DIP', chain=True)
    {(u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'): '', (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'E', u'1n8j', u'F', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'): '', (u'1n8j', u'I', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD'): '', (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'): '', (u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'): ''}
    """
    interactions = {}
    number_of_interactions = 0
    
    # NOTE: JENA has only PDB ids - without chains
    if chain:
        # without including JENA, we can get DIP and 3DID entries directly
        for entry in source:
            interactions[entry] = ''
            number_of_interactions += 1
    else:
        for entry in source:
            # Take only PDB ids (without chains), see NOTE above
            interactions[entry[0]] = ''
            interactions[entry[2]] = ''
            number_of_interactions += 2

    log_results.info('Number of %s interactions: %s' % (kind, number_of_interactions))
    
    return interactions


def find_overlaps(dip_interactions, three_did_interactions, jena_interactions=None, jena=False):
    """Returns number of overlapping iternactions from 1,2 or 3 datasets.
    Writes to FILE (results/overlapping-DIP-3DID.fa) overlapping interactions from DIP and 3DID.
    
    * **dip_interactions** list with interactions from DIP database.
    * **three_did_interactions** list with interactions from 3DID database.
    * **jena_interactions** list with PDBs from JENA database grouped by species.
    
    >>> find_overlaps({(u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'): '', (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'E', u'1n8j', u'F', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'): '', (u'1n8j', u'I', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD'): '', (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'): '', (u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'): ''}, {(u'1n8j', u'C', u'1n8j', u'X', u'DDDDRKKKRKDKDDDD'): '', (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'E', u'666j', u'F', u'DDDDDRKKRKWDKDDD'): '', (u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'): '', (u'1n8Q', u'i', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD'): '', (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'): '', (u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'): ''})
    4
    
    >>> find_overlaps({u'1N8j': '', u'': '', u'1ssj': ''}, {u'1n8j': '', u'AA66': '', u'1ssj': ''}, {u'1n8j': '', u'aa8j': '', u'1ssj': ''}, jena=True)
    (1, 2)
    
    """
    try:
        results_handler = open('results/overlapping-DIP-3DID.fa', 'w')
        # FIXME think of some better place, after installing this package by setup.py
    except IOError:
        log_load.exception('Problems with creating file: %s' % results_handler)

    # Find interactions overlapping in two sets
    if jena:
        # Find overlaps in DIP and JENA
        overlapping_dip_jena = 0
        for k in jena_interactions.keys():
            if k in dip_interactions.keys():
                to_write = '> %s\n' % k
                log_results.info('Overlapping DIP-JENA: %s' % to_write)
                overlapping_dip_jena += 1
        log_results.info('Number of overlapping DIP-JENA: %s' % overlapping_dip_jena)

        # Find overlaps in 3DID and JENA
        overlapping_3did_jena = 0
        for k in jena_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n' % k
                log_results.info('Overlapping 3DID-JENA: %s' % to_write)
                overlapping_3did_jena += 1
        log_results.info('Number of overlapping 3DID-JENA: %s' % overlapping_3did_jena)
        
        return overlapping_dip_jena, overlapping_3did_jena

    else:
        # Find overlaps in DIP and 3DID
        overlapping_dip_3did = 0
        for k in dip_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n%s\n' % (k, three_did_interactions[k])
                results_handler.write(to_write)
                overlapping_dip_3did += 1
        log_results.info('Number of overlapping DIP-3DID: %s' % overlapping_dip_3did)
        
    results_handler.close()
    log_results.info('Results written to: %s' % results_handler.name)
    
    return overlapping_dip_3did


def compare_interactions(dip_interactions_source=None, three_did_interactions_source=None, jena_interactions_source=None, jena=False):
    """Take interactions from one set (DIP, 3DID or JENA) and find overlapping interactions in the other one.
    Final results will be written here in fasta format, where 1st line is: interactor's PDB1chain1 - PDB2chain2
    
    * **dip_interactions_source** list of interactions from DIP.
    * **three_did_interactions_source** list of interactions from 3DID.
    * **jena_interactions_source** list of PDBs from JENA, grouped by species.
    * **jena** if True, all processing will not use PDB's chains information.

    >>> compare_interactions(dip_interactions_source=[(u'1n8j', u'A', u'1ssj', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'1n8j', u'F', u'DDDDDRKKRKWDKDDD'), (u'1n8j', u'G', u'1n8j', u'H', u'DDDRKKRKKDDD'), (u'1n8j', u'I', u'1n8j', u'J', u'DDDDRRKKRKDRDDDD')], three_did_interactions_source=[(u'1n8j', u'V', u'1n8j', u'B', u'NNERNNNERNNNVE'), (u'1n8j', u'C', u'1n8j', u'D', u'DDDDRKKKRKDKDDDD'), (u'1n8j', u'E', u'aa8j', u'X', u'DDDDDRKKRKWDKDDD')])
    """
    # TODO think of possible scanarios here and adjust it approprietly
    # If user wants to include DIP interactions in comparision...
    if dip_interactions_source:
        # If user wants to compare datasets from JENA...
        if jena:
            dip_interactions = get_pdbid_chain(dip_interactions_source, kind='DIP', chain=False)
        else:
            dip_interactions = get_pdbid_chain(dip_interactions_source, kind='DIP', chain=True)

    # If user wants to include 3DID interactions in comparision...
    if three_did_interactions_source:
        # If user wants to compare datasets from JENA...
        if jena:
            three_did_interactions = get_pdbid_chain(three_did_interactions_source, kind='3DID', chain=False)
        else:
            three_did_interactions = get_pdbid_chain(three_did_interactions_source, kind='3DID', chain=True)
            
    find_overlaps(dip_interactions, three_did_interactions)

    # If user wants to include JENA interactions in comparision...
    if jena_interactions_source:
        jena_interactions = get_pdbid_chain(jena_interactions_source, kind='JENA', chain=False)

        find_overlaps(dip_interactions, three_did_interactions, jena_interactions=jena_interactions, jena=True)


def output_fasta_file(most_interacting_interfaces, true_negatives_set=False):
    """Creates FASTA file with true positives OR true negatives from most interacting pairs of 3DID domains.
    If *true_negatives_set* is True, output will contain shuffled interacting domains (to mimic true negatives).
    
    * **most_interacting_interfaces**  list with pairs of interacting PDBs, chains, their corresponding sequences and joined interfaceself.
    * **true_negatives_set** if True, output will contain shuffled interacting domains.
    
    >>> output_fasta_file([(u'12e8', u'H', u'12e8', u'L', u'KKKDDKQQQDDTAFDDNNKFDPFF', u'KKKDDKQQQDDT', u'AFDDNNKFDPFF'), (u'12e8', u'M', u'12e8', u'P', u'ATGLKKHHHHTFFFFFFFPPAVQSSSPFFVSTNNTSTFSATSMSSASLTFFN', u'ATGLKKHHHHTFFFFFFFPPAVQSSS', u'PFFVSTNNTSTFSATSMSSASLTFFN'), (u'15c8', u'H', u'15c8', u'L', u'PSFFFFFFNNNLSSSAATTTSSMSTAKTLGFSSHSHVFPAFPHTFHFFFQ', u'PSFFFFFFNNNLSSSAATTTSSMST', u'AKTLGFSSHSHVFPAFPHTFHFFFQ'), (u'1a0q', u'H', u'1a0q', u'L', u'ATLGLKKHHHHTFFFFFFPPAVLQQQSSSPFFFVSTNNDSTFSWTSSSWSLLGLTFFN', u'ATLGLKKHHHHTFFFFFFPPAVLQQQSSS', u'PFFFVSTNNDSTFSWTSSSWSLLGLTFFN'), (u'1a1m', u'A', u'1a1m', u'B', u'YYYPPLLATTLLLKKHHHHHHTFFFFFFPPAVVVQQTSSSSTSEQSEVFPFNFVTSTNNTDTSTFSWTSSSWSLNSVLLFSFNN', u'YYYPPLLATTLLLKKHHHHHHTFFFFFFPPAVVVQQTSSSST', u'SEQSEVFPFNFVTSTNNTDTSTFSWTSSSWSLNSVLLFSFNN')])

    """
    # Create FASTA file with interacting domain pairs interfaces sequence
    if true_negatives_set:
        try:
            fasta_output = open('results/most_interacting_domain_pairs_interfaces-TN.fa', 'w')
        except IOError:
            log_load.exception("Unable to create a file: %s " % "results/most_interacting_domain_pairs_interfaces-TN.fa")
            
        interactors = []
        
        # Put each interactor from interacting pair of domains in one list
        for entry in most_interacting_interfaces:
            pdb_one = entry[0].strip()
            chain_one = entry[1].strip()
            seq_one = entry[5].strip()
            
            interactors.append((pdb_one, chain_one, seq_one))

            pdb_two = entry[2].strip()
            chain_two = entry[3].strip()
            seq_two = entry[6].strip()
            
            interactors.append((pdb_two, chain_two, seq_two))
        
        # Randomly choose two interactors and store them as (falsely) interacting pair
        for i in range(len(interactors)/2):
            interactor_one = random.choice(interactors)
            interactor_two = random.choice(interactors)
            
            pdb_one = interactor_one[0].strip()
            chain_one = interactor_one[1].strip()
            seq_one = interactor_one[2].strip()

            pdb_two = interactor_two[0].strip()
            chain_two = interactor_two[1].strip()
            seq_two = interactor_two[2].strip()
        
            to_write = '> %s%s - %s%s\n%s%s\n' % (pdb_one, chain_one, pdb_two, chain_two, seq_one, seq_two)
            fasta_output.write(to_write)
    else:
        try:
            fasta_output = open('results/most_interacting_domain_pairs_interfaces.fa', 'w')
            # FIXME think of some better place, after installing this package by setup.py
        except IOError:
            log_load.exception("Unable to create a file: %s " % "results/most_interacting_domain_pairs_interfaces.fa")

        for entry in most_interacting_interfaces:
            pdb_one = entry[0].strip()
            chain_one = entry[1].strip()
            pdb_two = entry[2].strip()
            chain_two = entry[3].strip()
            interface = entry[4].strip()

            to_write = '> %s%s - %s%s\n%s\n' % (pdb_one, chain_one, pdb_two, chain_two, interface)
            fasta_output.write(to_write)
    fasta_output.close()


if __name__ == "__main__":
    try:
        import nose
        nose.main(argv=['', '--verbose', '--with-doctest', '--with-coverage', '--cover-inclusive', '--cover-package=PPIM', '--detailed-errors', '--with-profile'])
    except ImportError:
        raise Exception("This package uses nose module for testing (which you do not have installed).")
