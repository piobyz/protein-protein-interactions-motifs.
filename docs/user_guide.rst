==========
User Guide
==========

Workflow
********

1. assume we have downloaded \*.mif25 files from DIP for every species

1a. \*.mif25 files need to be parsed to obtain DB/DIP-\*.db files (DIP.py for interactors and interactions
parsing and DBDIP.py for Structures and UniProt mapping)

2. sqlite3 DIP-Ecoli.db < ../PPIM/DIP-both_interacting-detailed.sql (change .output inside the SQL file)

3. now we have PDB1|chain1|PDB2|chain2 for every species in \*.output files

4. python DIP-both_interacting-reverse.py ../DB/Interacting_PDBs-DIP-in-3DID/Ecoli.output

5. run once: sqlite3 3did_simple.db < ../PPIM/3DID-interacting-PDB_chain.sql (produces 3DID-all-interacting-PDB_chain_seq.out)

6. Now, we have Ecoli.output-reversed-without-duplicates.out-overlapping-3DID.fa with overlapping PDBs in \*.fa file ready for SVM

7. In order to compare overlapping PDBs (without chains in JENA case) from *the same species* in DIP, 3DID and JENA:

- prepare file with PDBs from DIP: DIP-single_line-PDB.sql (change .output and concatenate PDB1 and PDB2!!)

- prepare 3DID (once only): 3DID-first_interactor-PDBchain.sql

- (change .output and make sure that p1.name and p2.name are run and then cat output1 output2 > final.output are concatenated)

8. JENA single line PDBs are prepared manually copying PDBs directly from their site and extracting PDB IDs, results stored in /JENA

9. Finally, run compare_pdb_list.py with DIP vs 3DID, DIP vs JENA, JENA vs 3DID

10. To find most interacting pair of domains: 3DID-most_interacting_domains.sql

11. To retrieve all joined sequences for the best pair above: 2nd query in the same file(3DID-most_interacting_domains.sql).

12. To prepare fasta file from the results above: make_fasta.py

13. Run SVM classifier and calculate sequence identity %.


Scenarios
*********

Analysis of Protein-Protein Interactions specific to species.
-------------------------------------------------------------

- User has downloaded a \*.mif25 file(s) from DIP (OR they should be provided with the package?)
  File contains interactions between proteins and other info (TODO enumerate them)

- Based on that file User wants to check the quality of the SVM classifier (description here...)

NOTE: intersection of interactions in DIP and 3DID is very small.

Additional input for classifier is provided: ... describe the 3DID Domains idea...

Steps taken by the package
--------------------------

1. User need to run Python script from the command line by typing:
python workflow.py [options] <path to mif25 file>

2. Additionally, (copy a help from workflow.py)

a) if User wants to include comparison between DIP, 3DID and JENA datasets concerning amount of interactions in each
dataset he\she should type:
python package_name.py -c <path to mif25 file>

b) if JENA dataset should be included in comparison User should type:
python package_name.py -c -j <path to JENA file> <path to mif25 file>
where JENA file should contain interactions from a particular species
[TODO this will be provided by the package most likely]

c) if User wants to use 3DID dataset (as advised in sec... above) he\\she should type:
python package_name.py -m NUMBER <path to mif25 file>
If no NUMBER is provided, 1 is default value, so the first, most interacting pair of domains will be used to build a classifier.


Species analyzed after first run of the package
***********************************************

Because there is a mapping between PDB and UniProt needed to be performed, first run of the script is slow (about 80 minutes).
TODO Or maybe it's better to include DB with this mapping? And only those who want to have up to date mapping might download current mapping from UniProt FTP and run creation of the newest version by themselves?
