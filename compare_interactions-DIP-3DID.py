'''DIP consists of interactions grouped by species. 3DID has no distinction.
Both DBs take into account which domains interacts with each other but only
3DID lists residues from interface.
To retrieve interface's sequence group by species one has to map interactions
from DIP into 3DID.
For fast comparisions purpose we use dictionaries containing interacting pdb|chain as keys.
'''

if __name__ == '__main__':
    dip_interactions_handler = open('../DB/Interacting_PDBs/Hsapi-reversed-without-duplicates.out', 'r')
    three_did_interactions_handler = open('../DB/3DID-all-interacting-PDB_chain.out', 'r')
    
    dip_interactions = {}
    three_did_interactions = {}
    
    for line in dip_interactions_handler:
        dip_interactions[line.strip()]=''
    print len(dip_interactions)
        
    for line in three_did_interactions_handler:
        pdb_chain = '|'.join(line.split('|')[:-1])
        interface = line.split('|')[-1] 
        three_did_interactions[pdb_chain]=interface
    print len(three_did_interactions)
    
    for k in dip_interactions.keys():
        if three_did_interactions.has_key(k):
            print k, three_did_interactions[k]
