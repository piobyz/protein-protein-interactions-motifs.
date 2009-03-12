#!/usr/bin/env python
'''Compare two single-line PDB lists and output a new list which has only those entries
which are present on  both input lists.
'''

__author__ = "Piotr Byzia"
__credits__ = ["Hugh Shanahan"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Piotr Byzia"
__email__ = "piotr.byzia@gmail.com"
__status__ = "Prototype"


import sys

if __name__ == '__main__':
    # CLI arguments maintaince
    if(len(sys.argv) == 1):
        print 'Provide two PDB single-line lists as arguments.'
        sys.exit(1)
    elif(len(sys.argv) == 2):
        print 'Provide two PDB single-line lists as arguments.'
        sys.exit(1)
    elif(len(sys.argv) == 3):
        try:
            dip_pdb_list = open(sys.argv[1], 'r')
        except IOError:
            'There is no such a file on path: ', argv[1]
            sys.exit(1)
        try:
            threedid_pdb_list = open(sys.argv[2], 'r')
        except IOError:
            'There is no such a file on path: ', argv[2]
            sys.exit(1)
    else:
        'See source for usage.'
        sys.exit(1)
    
    
    ##### TODO correct var names, so that won't be confusing what is being
    #           calculated.
    ##### TODO The same with output file name and prints
    
    
    
    # Where to write all entries present in both lists.
    results_handler = open('../DB/PDB-overlapping_entries-JENA-in-3DID.out', 'w')
    overlapping = 0
    
    # Transfer both lists into dictionary for speed and convenience
    threedid_pdb = {}
    licznik=0
    for line in threedid_pdb_list:
        threedid_pdb[line.strip()] = ''
        licznik += 1
    
    dip_pdb = {}
    licznik_2 = 0
    for line in dip_pdb_list:
        dip_pdb[line.strip()] = ''
        licznik_2 += 1
    
    # Take each line from 1st list (smaller) and see if its present in the bigger one
    for entry in dip_pdb:
        if entry in threedid_pdb:
            to_write = '%s\n' % (entry)
            results_handler.write(to_write)
            overlapping += 1
    results_handler.close()

    print 'Found %s entries present in both lists.' % overlapping
    print '1st set size: DISTINCT ', len(dip_pdb), ' ALL: ' ,licznik_2
    print '2nd set size: DISTINCT ', len(threedid_pdb), ' ALL: ', licznik
