#!/usr/bin/env python
'''DIP consists of interactions grouped by species. 3DID has no distinction.
Both DBs take into account which domains interacts with each other but only
3DID lists residues from interface.
To retrieve interface's sequence group by species one has to map interactions
from DIP into 3DID.
For fast comparisions purpose we use dictionaries containing interacting pdb|chain as keys.
'''

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import sys

three_did_interactions_handler = open('../DB/3DID-all-interacting-PDB_chain.out', 'r')

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        print 'Provide one of the DIP *.output interactions file as an argument. \
        Best, after running through DIP-both_interacting-reverse.py'
        # TODO Perform this step in this script.
        sys.exit(1)
    elif(len(sys.argv) == 2):
        try:
            dip_interactions_handler = open(sys.argv[1], 'r')
            results_handler = open(str(sys.argv[1]) + '-overlapping-3DID.results', 'w')
        except IOError:
            'There is no such a file on path: ', argv[1]
            sys.exit(1)
    else:
        'See source for usage.'
        sys.exit(1)

    dip_interactions = {}
    three_did_interactions = {}

    for line in dip_interactions_handler:
        dip_interactions[line.strip()]=''
    print 'DIP interactions: ', len(dip_interactions)

    for line in three_did_interactions_handler:
        pdb_chain = '|'.join(line.split('|')[:-1])
        interface = line.split('|')[-1]
        three_did_interactions[pdb_chain]=interface
    print 'All 3DID interactions: ', len(three_did_interactions)

    for k in dip_interactions.keys():
        if k in three_did_interactions:
            to_write = '%s %s\n' % (k, three_did_interactions[k])
            results_handler.write(to_write)
