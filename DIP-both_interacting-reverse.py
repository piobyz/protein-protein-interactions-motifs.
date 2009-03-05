#!/usr/bin/env python
"""Prepare interactions to compare with compare_interactions-DIP-3DID.py
"""

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import sys
from compare_interactions_DIP_3DID import compare_interactions


def uniq(alist):
    set = {}
    return [set.setdefault(e, e) for e in alist if e not in set]


def create_reversed_interactions(dip_interactions_source):
    """Takes a list of interacting PDB1|chain1|PDB2|chain2 and appends PDB2|chain2|PDB1|chain1
    finally removing duplicates."""
    with_possible_duplicates = []

    # Because we need to consider interactions where 2 pdb+chain are listed in the reverse order
    # we want to create a non redundant list with all interactions reversed (as well as non reversed ones).
    for line in dip_interactions_source:
        interacting_pdbs = line.split('|')

        first_pdb = interacting_pdbs[0].strip()
        first_chain = interacting_pdbs[1].strip()
        second_pdb = interacting_pdbs[2].strip()
        second_chain = interacting_pdbs[3].strip()

        reversed_interaction = '%s|%s|%s|%s\n' % (second_pdb, second_chain, first_pdb, first_chain)

        with_possible_duplicates.append(line.strip())
        with_possible_duplicates.append(reversed_interaction.strip())

    dip_interactions_source.close() # FIXME this looks bad

    without_duplicates = uniq(with_possible_duplicates)
    print 'Found %s duplicates.' % (len(with_possible_duplicates) - len(without_duplicates))

    without_duplicates_file_name = str(sys.argv[1]) + '-reversed-without-duplicates.out'
    without_duplicates_file_handler = open(without_duplicates_file_name, 'w')

    for interaction in without_duplicates:
        without_duplicates_file_handler.write(interaction+'\n')

    without_duplicates_file_handler.close()
    
    return without_duplicates_file_name


if __name__ == '__main__':
    # CLI arguments maintaince
    if(len(sys.argv) == 1):
        print 'Provide one of the DIP *.output interactions file as an argument.'
        sys.exit(1)
    elif(len(sys.argv) == 2):
        try:
            # In this file there are (hopefully) all interactions retrieved from DIP regarding single species.
            dip_interactions_by_species = open(sys.argv[1], 'r')
        except IOError:
            'There is no such a file on path: ', argv[1]
            sys.exit(1)
    else:
        'See source for usage.'
        sys.exit(1)

    reverted_interactions = create_reversed_interactions(dip_interactions_by_species)
    compare_interactions(reverted_interactions)
