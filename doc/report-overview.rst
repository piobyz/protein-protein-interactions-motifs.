==================================================
 Protein-Protein Interactions (PPI) Classification
==================================================

1. Simon, Baldo and Richard's dataset
=====================================

Motivation and Approach
************************
This DB contains I1 dataset described on http://bmbpcu36.leeds.ac.uk/~bmb4sjc/ as:
"42 interactions confirmed by experimental evidence (i.e. presence in DIP)".

There is another set, I2, described as:
"High confidence set, 1,297 interactions that have a Patch Overlap Score greater
than 0.9 and a Clash Score less than 20.".
We didn't want to include that one, while it contains only a putative interactions and
for purpose of classification by SVM we needed really 100% confidence, "gold standard" set.

I1 consists of 24 seeding interactions.
Each of this interaction involves 2 putatively interacting chains which were chosen based on their
similarity with interacting proteins from DIP (with known 3D structure, i.e. present in the PDB).

Patches from each of 2 aligned pairs of interacting proteins were of interest to us.
(6.600 of them, parsed from http://bmbpcu36.leeds.ac.uk/~bmb4sjc/Project/alignments/)

For the purpose of quick and convenient access to data we created a database,
schema is in DB_schema.pdf:

.. image:: DB_schema.pdf
   :height: 100
   :width: 200
   :scale: 50

DB mapping and parsing workflow are in DB.py and PPIMotifs.py, respectively.
SQL query used to find distinctive patches: Distinct_patches_307.sql

Results
*******
One of our observation is that there is a very small number of distinctive seeding proteins in I1 dataset.
If we are correct there are only **161** of them coming from distinctive PDB's (including different chains) files.

As explained in section "Predicting new interactions by Sequence Search of Interface Patterns (SSIP)"
non-identical interacting proteins from SPIN-PP database (which is subset of the PDB containing
PPI complexes as I understand) has been used.

Baldo's response:
"The number of proteins in I1 is very small because it has the highest restriction, they have to have
similarities with experimentally known interactions (usually this means these interactions can be directly modelled
without docking, there is an example in the picture of the article).

In SSIP there were no restrictions (except for the patch), but in I1, I2 and I3 there are structural restrictions,
and strongest is for I1."


2. DIP with 3DID
================

Motivation and Approach
************************
DIP has datasets with interactions grouped by species (MIF 2.5 format, 
http://dip.doe-mbi.ucla.edu/dip/Download.cgi?SM=7)
Provided XML files have DIP ID for interactors and interactions and, among others, UniProt IDs
which were mapped to the corresponding PDB|chain using mapping from
http://www.bioinf.org.uk/pdbsws/pdbsws_chain.txt
Database's schema is in file: DIP_schema, DB's files are in: DB/DIP-species/\*.db

.. image:: DIP_schema.pdf
   :height: 100
   :width: 200
   :scale: 50

In order to prepare input files for the SVM we needed sequence from the interface of each interaction.
This information were absent in DIP but present in 3DID, where each interacting pair of residues were listed
grouped by Pfam domain and PDB|chain.

We didn't want to use only 3DID because there are no grouping by species provided,
so dataset would be huge(about 120 000 interactions) and non-specific.

To combine the power of DIP with 3DID we used PDB|chain, present both in DIP (after mapping described above)
and 3DID.
Additionally, only a fraction of DIP interactors has known 3D structure, so another idea might be to use NACCESS
to calculate which residues occupy surface of protein and based on that assume that those residues are involved
in creating interface (wrapper for NACCESS is available in BioPython).

3DID database schema is in 3DID_schema:

.. image:: 3DID_schema.pdf
   :height: 100
   :width: 200
   :scale: 50

For each species (from each \*.db file) there were files with PDB1|chain1|PDB2|chain2 interactions prepared.
Subsequently, the content of file above was compared against all interactions from 3DID and corresponding interactions were saved
together with corresponding sequence.

**\*.db** files were prepared by DIP.py and DBDIP.py


TODO: logging all the intermediate and final results (stats + were the output files were written)

TODO: Create nice looking report from logged results + documentation / doctests using Sphinx

TODO: Write /tests using nose

TODO: create setup.py

TODO: !!! check whether there are some issue with case sensitive PDB IDs in every file I use

Workflow:
1. assume we have downloaded \*.mif25 files from DIP for every species

1a. Mif25 files need to be parsed to obtain DB/DIP-\*.db files (DIP.py for interactors and interactions
parsing and DBDIP.py for Structures and UniProt mapping)

2. sqlite3 DIP-Ecoli.db < ../PPIM/DIP-both_interacting-detailed.sql (change .output inside the SQL file)

3. now we have PDB1|chain1|PDB2|chain2 for every species in \*.output files

4. python DIP-both_interacting-reverse.py ../DB/Interacting_PDBs-DIP-in-3DID/Ecoli.output

5. run once: sqlite3 3did_simple.db < ../PPIM/3DID-interacting-PDB_chain.sql (produces 3DID-all-interacting-PDB_chain_seq.out)

6. Now, we have Ecoli.output-reversed-without-duplicates.out-overlapping-3DID.fa with overlapping PDBs in \*.fa file ready for SVM

7. In order to compare overlapping PDBs (without chains) from *the same species* in DIP, 3DID and JENA:

- prepare file with PDBs from DIP: DIP-single_line-PDB.sql (change .output and concatenate PDB1 and PDB2!!)

- prepare 3DID (once only): 3DID-first_interactor-PDBchain.sql

- (change .output and make sure that p1.name and p2.name are run and then cat output1 output2 > final.output are concatenated)

8. JENA single line PDBs are prepared manually copying PDBs directly from their site and extracting PDB IDs, results stored in /JENA

9. Finally, run compare_pdb_list.py with DIP vs 3DID, DIP vs JENA, JENA vs 3DID

10. To find most interacting pair of domains: 3DID-most_interacting_domains.sql

11. To retrieve all joined sequences for the best pair above: 2nd query in the same file(3DID-most_interacting_domains.sql).

12. To prepare fasta file from the results above: make_fasta.py

13. Run SVM classifier and calculate sequence identity %.


\*.output files were generated by command:
 *sqlite3 DIP-Ecoli.db < ../PPIM/DIP-both_interacting-detailed.sql*

Interactions from 3DID (3DID-all-interacting-PDB_chain.out) were generated by:
 *sqlite3 3did_simple.db < ../PPIM/3DID-interacting-PDB_chain.sql*

Having \*.output and 3DID-all-interacting-PDB_chain.out in place we were able to run workflow
which produced resulting \*.fa file with all overlapping interactions. For example, for E.coli:

 *python DIP-both_interacting-reverse.py ../DB/Interacting_PDBs/Ecoli.output*

In order to check how similar all the 3DID sequences are we used PISCES service, which given some cutoff returns
a subset of all provided PDBchain where sequence percentage identity is less or equal to cutoff %.

 *http://dunbrack.fccc.edu/Guoli/PISCES.php*

For **90% cutoff** PISCES returned 10 373 out of 110 594 (~**9.5%**).
For **75% cutoff** 9 343 (~**8.5%**) structures were returned (out of 110 594).

Because mapping from DIP to 3DID interactions were very poor we wanted to verify those results.
Jena Library was used, which among others, provides mapping of PDB to species.

 *http://www.fli-leibniz.de/IMAGE.html*

Results
*******
Workflow above were applied to all species from DIP and overlapping PDB|chain are very rare.
For example: M.Musculus **7** overlapping PDB|chain, H.Sapiens - **31**. There were **93** interactions
from DIP concerning mouse, and **718** concerning human. Reversed interactions were also included
(pdb1|chain1 <->pdb2|chain2 -> pdb2|chain2 <-> pdb1|chain1 ; <-> meaning 'interacts with')
in comparisons. Total number of 3DID interactions were **99160**.

C.elegans
---------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/Celeg.output-reversed-without-duplicates.out-overlapping-3DID.fa***
       0 Interacting_PDBs-DIP-in-3DID/Celeg.output-reversed-without-duplicates.out-overlapping-3DID.fa

0 interactions

***$ python compare_pdb_list.py ../DB/DIP-species/C.elegans-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **4** entries present in both lists.

DIP set size: DISTINCT  **5**  ALL:  6

3DID set size: DISTINCT  **27132**  ALL:  247400


***$ python compare_pdb_list.py ../DB/DIP-species/C.elegans-single_line-PDB.txt ../DB/JENA/pdb_by_species-C.elegans.txt***

Found **5** entries present in both lists.

DIP set size: DISTINCT  **5**  ALL:  6

JENA set size: DISTINCT  **98**  ALL:  98


***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-C.elegans.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **43** entries present in both lists.

JENA set size: DISTINCT  **98**  ALL:  98

3DID set size: DISTINCT  **27132**  ALL:  247400


D.melanogaster
----------------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/Dmela.output-reversed-without-duplicates.out-overlapping-3DID.fa***
       8 Interacting_PDBs-DIP-in-3DID/Dmela.output-reversed-without-duplicates.out-overlapping-3DID.fa

8 / 2 = 4 interactions (it's FASTA file, thus division)

***$ python compare_pdb_list.py ../DB/DIP-species/D.melanogaster-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out ***

Found **16** entries present in both lists.

DIP set size: DISTINCT  **30**  ALL:  50

3DID set size: DISTINCT  **27132**  ALL:  247400


***$ python compare_pdb_list.py ../DB/DIP-species/D.melanogaster-single_line-PDB.txt ../DB/JENA/pdb_by_species-D.melanogaster.txt***

Found **20** entries present in both lists.

DIP set size: DISTINCT  **30**  ALL:  50

JENA set size: DISTINCT  **337**  ALL:  337


***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-D.melanogaster.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **171** entries present in both lists.

JENA set size: DISTINCT  **337**  ALL:  337

3DID set size: DISTINCT  **27132**  ALL:  247400


E.coli
------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/Ecoli.output-reversed-without-duplicates.out-overlapping-3DID.fa***
      28 Interacting_PDBs-DIP-in-3DID/Ecoli.output-reversed-without-duplicates.out-overlapping-3DID.fa

28 / 2 = 14 interactions

***$ python compare_pdb_list.py ../DB/DIP-species/E.coli-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **115** entries present in both lists.

DIP set size: DISTINCT  **169**  ALL:  542

3DID set size: DISTINCT  **27132**  ALL:  247400

***$ python compare_pdb_list.py ../DB/DIP-species/E.coli-single_line-PDB.txt ../DB/JENA/pdb_by_species-E.coli.txt***

Found **163** entries present in both lists.

DIP set size: DISTINCT  **169**  ALL:  542

JENA set size: DISTINCT  **4847**  ALL:  4847

***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-E.coli.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **2807** entries present in both lists.

JENA set size: DISTINCT  **4847**  ALL:  4847

3DID set size: DISTINCT  **27132**  ALL:  247400


H.pylori
--------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/Hpylo.output-reversed-without-duplicates.out-overlapping-3DID.fa***
       0 Interacting_PDBs-DIP-in-3DID/Hpylo.output-reversed-without-duplicates.out-overlapping-3DID.fa

0 interactions

***$ python compare_pdb_list.py ../DB/DIP-species/H.pylo-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **4** entries present in both lists.

DIP set size: DISTINCT  **6**  ALL:  8

3DID set size: DISTINCT  **27132**  ALL:  247400

***$ python compare_pdb_list.py ../DB/DIP-species/H.pylo-single_line-PDB.txt ../DB/JENA/pdb_by_species-H.pylori.txt***

Found **5** entries present in both lists.

DIP set size: DISTINCT  **6**  ALL:  8

JENA set size: DISTINCT  **165**  ALL:  165

***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-H.pylori.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **102** entries present in both lists.

JENA set size: DISTINCT  **165**  ALL:  165

3DID set size: DISTINCT  **27132**  ALL:  247400


H.sapiens
---------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/Hsapi.output-reversed-without-duplicates.out-overlapping-3DID.fa***
      62 Interacting_PDBs-DIP-in-3DID/Hsapi.output-reversed-without-duplicates.out-overlapping-3DID.fa

62 / 2 = 31 interactions

***$ python compare_pdb_list.py ../DB/DIP-species/H.pylo-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **4** entries present in both lists.

DIP set size: DISTINCT  **6**  ALL:  8

3DID set size: DISTINCT  **27132**  ALL:  247400

***$ python compare_pdb_list.py ../DB/DIP-species/H.pylo-single_line-PDB.txt ../DB/JENA/pdb_by_species-H.pylori.txt***

Found **5** entries present in both lists.

DIP set size: DISTINCT  **6**  ALL:  8

JENA set size: DISTINCT  **165** ALL:  165

***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-H.pylori.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **102** entries present in both lists.

JENA set size: DISTINCT  **165**  ALL:  165

3DID set size: DISTINCT  **27132**  ALL:  247400


M.musculus
----------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/M.musculus.output-reversed-without-duplicates.out-overlapping-3DID.fa***
      14 Interacting_PDBs-DIP-in-3DID/M.musculus.output-reversed-without-duplicates.out-overlapping-3DID.fa

14 / 2 = 7

***$ python compare_pdb_list.py ../DB/DIP-species/M.musculus-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **75** entries present in both lists.

DIP set size: DISTINCT  **125**  ALL:  192

3DID set size: DISTINCT  **27132**  ALL:  247400

***$ python compare_pdb_list.py ../DB/DIP-species/M.musculus-single_line-PDB.txt ../DB/JENA/pdb_by_species-m.musculus.txt***

Found **78** entries present in both lists.

DIP set size: DISTINCT  **125**  ALL:  192

JENA set size: DISTINCT  **2557**  ALL:  2557

***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-m.musculus.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **1499** entries present in both lists.

JENA set size: DISTINCT  **2557**  ALL:  2557

3DID set size: DISTINCT  **27132**  ALL:  247400

S.cerevisiae
------------
Interactions in DIP present in 3DID:

***$ wc -l Interacting_PDBs-DIP-in-3DID/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa***
     112 Interacting_PDBs-DIP-in-3DID/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa

112 / 2 = 56

***$ python compare_pdb_list.py ../DB/DIP-species/S.cerevisiae-single_line-PDB.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **201** entries present in both lists.

DIP set size: DISTINCT  **359**  ALL:  1644

3DID set size: DISTINCT  **27132**  ALL:  247400

***$ python compare_pdb_list.py ../DB/DIP-species/S.cerevisiae-single_line-PDB.txt ../DB/JENA/pdb_by_species-S.cerevisiae.txt***

Found **341** entries present in both lists.

DIP set size: DISTINCT  **359**  ALL:  1644

JENA set size: DISTINCT  **1610**  ALL:  1610

***$ python compare_pdb_list.py ../DB/JENA/pdb_by_species-S.cerevisiae.txt ../DB/3DID/3DID-single_line-PDB.out***

Found **809** entries present in both lists.

JENA set size: DISTINCT  **1610**  ALL:  1610

3DID set size: DISTINCT  **27132**  ALL:  247400





2009-03-11 14:26:16,985 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(78)[motifkernel.loadData]: INFO Dividing data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa into TEST +: 14, TRAINING +: 42
2009-03-11 14:26:36,838 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(75)[motifkernel.loadData]: INFO Dividing test set into TEST +: 7, shuffled TEST -: 7
2009-03-11 14:26:40,943 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(99)[motifkernel.loadData]: INFO From data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa: TRAINING -: 42
2009-03-11 14:27:19,744 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-11 14:27:19,744 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====S: SVM (3, 0) 25 % training set====
2009-03-11 14:27:49,719 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-11 14:27:51,294 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 71.4286% (10/14) (classification)

2009-03-11 14:27:51,300 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 14:27:51,331 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 14:27:51,331 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-11 14:27:51,331 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====S: SVM (3, 0) 25 % training set====
2009-03-11 14:27:59,085 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 64.2857% (9/14) (classification)

2009-03-11 14:27:59,091 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 14:27:59,091 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 14:28:00,657 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-11 14:28:00,657 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (3, 1) 25 % training set====
2009-03-11 14:28:33,857 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-11 14:28:35,864 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 85.7143% (12/14) (classification)

2009-03-11 14:28:35,871 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 14:28:35,871 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 14:28:35,871 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-11 14:28:35,872 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (3, 1) 25 % training set====
2009-03-11 14:28:44,140 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 57.1429% (8/14) (classification)

2009-03-11 14:28:44,147 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 14:28:44,148 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 14:28:44,303 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(78)[motifkernel.loadData]: INFO Dividing data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa into TEST +: 14, TRAINING +: 42
2009-03-11 14:34:37,527 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(75)[motifkernel.loadData]: INFO Dividing test set into TEST +: 7, shuffled TEST -: 7
2009-03-11 14:36:00,196 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(99)[motifkernel.loadData]: INFO From data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa: TRAINING -: 42
2009-03-11 14:48:38,181 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-11 14:48:38,182 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====S: SVM (4, 0) 25 % training set====
2009-03-11 15:32:56,729 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-11 15:40:11,757 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 42.8571% (6/14) (classification)

2009-03-11 15:40:11,902 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 15:40:11,902 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 15:40:11,902 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-11 15:40:11,903 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====S: SVM (4, 0) 25 % training set====
2009-03-11 16:31:29,342 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 21.4286% (3/14) (classification)

2009-03-11 16:31:29,488 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 16:31:29,488 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 16:32:00,156 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-11 16:32:00,160 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (4, 1) 25 % training set====
2009-03-11 17:16:47,669 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-11 17:23:58,475 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 64.2857% (9/14) (classification)

2009-03-11 17:23:58,619 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 17:23:58,620 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 17:23:58,651 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-11 17:23:58,651 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (4, 1) 25 % training set====
2009-03-11 18:14:48,912 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 42.8571% (6/14) (classification)

2009-03-11 18:14:49,060 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 7, all negatives: 7
2009-03-11 18:14:49,060 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 14
2009-03-11 18:14:54,391 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(78)[motifkernel.loadData]: INFO Dividing data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa into TEST +: 14, TRAINING +: 42
2009-03-11 20:14:47,226 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(75)[motifkernel.loadData]: INFO Dividing test set into TEST +: 7, shuffled TEST -: 7
2009-03-11 20:41:59,734 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(99)[motifkernel.loadData]: INFO From data/S.cerevisiae.output-reversed-without-duplicates.out-overlapping-3DID.fa: TRAINING -: 42


Most interactions classifier 50% (3,0), (3,1)
--------------------------------
2009-03-16 13:06:40,734 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(78)[motifkernel.loadData]: INFO Dividing data/most_interactions.fa into TEST +: 939, TRAINING +: 940
2009-03-16 13:12:40,545 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(75)[motifkernel.loadData]: INFO Dividing test set into TEST +: 469, shuffled TEST -: 470
2009-03-16 13:15:23,947 /Users/piotr/Projects/Thesis/Spring/MotifKernel/preparedata.py(99)[motifkernel.loadData]: INFO From data/most_interactions.fa: TRAINING -: 940
2009-03-16 13:30:51,691 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-16 13:30:51,703 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====most_interactions: SVM (3, 0) 50 % training set====
2009-03-16 17:24:39,569 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-16 17:27:25,183 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 47.1778% (443/939) (classification)

2009-03-16 17:27:25,638 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 469, all negatives: 470
2009-03-16 17:27:25,641 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 939
2009-03-16 17:27:25,698 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-16 17:27:25,709 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(58)[motifkernel.svm]: INFO ====most_interactions: SVM (3, 0) 50 % training set====
2009-03-16 17:32:27,172 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 58.7859% (552/939) (classification)

2009-03-16 17:32:27,591 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 469, all negatives: 470
2009-03-16 17:32:27,594 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 939
2009-03-16 17:33:53,418 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(50)[motifkernel.svm]: INFO +++RADIAL KERNEL+++
2009-03-16 17:33:53,509 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (3, 1) 50 % training set====
2009-03-16 21:36:56,421 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(121)[motifkernel.svm]: INFO Training: extras/svm-train -c 0.03125 -g 0.0001220703125 output/libsvm_training.input.scale output/libsvm_training.input.model
2009-03-16 21:39:43,190 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 48.7753% (458/939) (classification)

2009-03-16 21:39:43,835 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 469, all negatives: 470
2009-03-16 21:39:43,883 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 939
2009-03-16 21:39:44,123 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(52)[motifkernel.svm]: INFO +++LINEAR KERNEL+++
2009-03-16 21:39:44,150 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(60)[motifkernel.svm]: INFO ====SVM (3, 1) 50 % training set====
2009-03-16 21:44:59,305 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(141)[motifkernel.svm]: INFO Accuracy = 63.6848% (598/939) (classification)

2009-03-16 21:44:59,734 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(167)[motifkernel.svm]: INFO Number of all positives: 469, all negatives: 470
2009-03-16 21:44:59,756 /Users/piotr/Projects/Thesis/Spring/MotifKernel/svm.py(176)[motifkernel.svm]: INFO Predicted labels length: 939





-- 3010|3010|101|101
-- 486|486|102|102
-- 2469|2469|102|102
-- 276|276|103|103
-- 43|43|105|105
-- 276|2628|105|105
-- 1065|1065|105|105
-- 1170|1170|105|105
-- 1644|1644|106|106
-- 3012|2628|107|107
-- 3417|1326|107|107
-- 2383|2384|108|108
-- 2800|2800|108|108
-- 61|62|109|109
-- 335|336|110|110
-- 699|699|110|110
-- 2716|2716|110|110
-- 99|3284|111|111
-- 1542|1543|112|112
-- 2023|2023|112|112
-- 49|49|113|113
-- 383|383|113|113
-- 2336|2337|113|113
-- 3103|3102|113|113
-- 214|214|114|114
-- 2263|2263|114|114
-- 2879|2880|116|116
-- 2698|2698|117|117
-- 122|129|118|118
-- 3125|3126|118|118
-- 641|642|119|119
-- 996|996|119|119
-- 423|423|120|120
-- 450|451|120|120
-- 1448|1448|120|120
-- 989|990|121|121
-- 1664|1661|121|121
-- 109|143|123|123
-- 142|143|123|123
-- 1482|1483|123|123
-- 2384|2384|123|123
-- 3009|3009|123|123
-- 3179|3180|123|123
-- 3452|3452|123|123
-- 841|841|124|124
-- 1094|1094|124|124
-- 458|458|126|126
-- 925|925|126|126
-- 1001|761|126|126
-- 2580|2580|126|126
-- 3242|3169|127|127
-- 3243|3169|127|127
-- 2193|2193|128|128
-- 2241|334|128|128
-- 987|989|129|129
-- 3242|3242|129|129
-- 3241|3241|130|130
-- 3121|3122|131|131
-- 207|208|132|132
-- 2055|2055|132|132
-- 2225|2226|132|132
-- 3241|3243|132|132
-- 2510|129|133|133
-- 1056|1056|134|134
-- 1285|1285|134|134
-- 1489|676|134|134
-- 595|595|135|135
-- 783|784|135|135
-- 2148|2148|135|135
-- 2621|2622|135|135
-- 3133|3120|137|137
-- 335|335|138|138
-- 544|544|138|138
-- 803|803|138|138
-- 1010|1010|138|138
-- 3172|3172|138|138
-- 3469|3469|138|138
-- 3324|3324|140|140
-- 890|890|142|142
-- 637|637|143|143
-- 2242|2242|143|143
-- 134|134|146|146
-- 142|142|146|146
-- 553|553|147|147
-- 3180|1183|148|148
-- 1845|1845|149|149
-- 3017|3018|149|149
-- 2477|2478|151|151
-- 3322|3322|151|151
-- 1803|1803|153|153
-- 845|2456|154|154
-- 1476|1476|154|154
-- 1860|554|154|154
-- 3235|3236|154|154
-- 3442|3442|155|155
-- 75|75|156|156
-- 459|459|156|156
-- 639|41|156|156
-- 3167|3167|156|156
-- 640|41|157|157
-- 1043|1043|157|157
-- 183|183|158|158
-- 431|431|158|158
-- 646|645|158|158
-- 364|364|159|159
-- 552|553|159|159
-- 1661|1661|159|159
-- 977|977|161|161
-- 2950|1017|161|161
-- 1519|1520|163|163
-- 2660|2660|163|163
-- 863|863|164|164
-- 1456|1458|165|165
-- 350|350|166|166
-- 553|554|166|166
-- 1904|1904|167|167
-- 274|274|168|168
-- 451|459|169|169
-- 1681|1681|169|169
-- 1804|1804|169|169
-- 142|109|170|170
-- 236|237|170|170
-- 1696|1696|173|173
-- 172|172|175|175
-- 893|894|176|176
-- 533|190|180|180
-- 1039|1017|180|180
-- 2|2|186|186
-- 1084|1084|186|186
-- 1111|1111|186|186
-- 204|205|187|187
-- 451|451|187|187
-- 2477|2477|190|190
-- 3395|3395|190|190
-- 1822|1822|195|195
-- 2281|2281|196|196
-- 25|25|197|197
-- 2869|945|197|197
-- 502|502|199|199
-- 573|572|203|203
-- 1925|1925|203|203
-- 384|384|204|204
-- 281|281|206|206
-- 664|664|210|210
-- 2926|3468|210|210
-- 1104|1104|217|217
-- 310|310|219|219
-- 987|990|219|219
-- 1458|1457|222|222
-- 2054|2054|222|222
-- 660|660|231|231
-- 122|122|234|234
-- 489|641|234|234
-- 761|311|234|234
-- 3434|1476|235|235
-- 2478|2478|237|237
-- 5|6|241|241
-- 311|311|241|241
-- 3242|3243|241|241
-- 3172|2907|242|242
-- 3513|3513|248|248
-- 393|393|249|249
-- 451|452|250|250
-- 700|700|250|250
-- 838|838|257|257
-- 945|945|261|261
-- 2334|2335|261|261
-- 2533|2533|263|263
-- 2299|2299|264|264
-- 177|178|267|267
-- 1475|1475|267|267
-- 1545|1545|272|272
-- 2071|2071|273|273
-- 2317|2317|278|278
-- 2286|2287|285|285
-- 275|276|294|294
-- 3234|3234|295|295
-- 1831|1831|298|298
-- 2969|2969|301|301
-- 1860|553|302|302
-- 315|315|306|306
-- 2215|2214|310|310
-- 517|517|322|322
-- 418|418|332|332
-- 334|334|333|333
-- 478|478|337|337
-- 3437|334|341|341
-- 1128|1128|344|344
-- 3566|3566|345|345
-- 174|174|348|348
-- 1820|1820|348|348
-- 486|1191|351|351
-- 1831|1832|372|372
-- 3241|3242|372|372
-- 700|701|377|377
-- 3240|3240|381|381
-- 890|891|386|386
-- 1|2|391|391
-- 2543|2543|394|394
-- 2926|3469|398|398
-- 3234|3236|398|398
-- 55|55|400|400
-- 1056|1464|405|405
-- 3234|3235|410|410
-- 210|210|421|421
-- 923|923|421|421
-- 3578|3578|424|424
-- 1814|1814|450|450
-- 3468|3469|455|455
-- 1992|1992|480|480
-- 821|821|494|494
-- 1061|1061|503|503
-- 1814|2940|523|523
-- 171|172|532|532
-- 2940|2940|532|532
-- 2267|2268|550|550
-- 3322|3323|551|551
-- 73|2969|570|570
-- 193|193|587|587
-- 926|926|592|592
-- 292|292|611|611
-- 405|405|615|615
-- 1925|1926|624|624
-- 676|676|779|779
-- 250|250|784|784
-- 489|640|828|828
-- 1943|1944|875|875
-- 1645|1645|1422|1422
-- 489|41|1520|1520
-- 73|73|1808|1808
-- 41|41|1848|1848
-- 489|489|1879|1879





3. IMEx
=======
To investigate. Seems that this is going to be a standard in describing PPI (DIP, IntAct, others)
XML is v. hard to read, but all necessary infos should be there.

Not many interactions included yet (about 1000, human curated (from literature)
and those sent by researchers together with publication).

Also, see e-mail from Lukasz Salwinski.

4. SCOPPI
=========
Looks good (i.e. rendered images with interface exposed) but does not provide any flat files.

5. PIBASE
=========
Looks OK, got flat files with interactions and sequences involved.
Also, see e-mail from Fred Davis describing columns in flat files.

6. STRING
=========
Nice looking, but no information about directly interacting domains / interfaces / sequences.

7. "Cataloging the Relationships..." review paper
=================================================


8. IntAct, MINT, BIND, others?
==============================

9. MODBASE, iPfam
=================


Final project
=============
1. Topics:
    a) RNA
    b) structure prediction (maybe connected with a?)
    c) Pathways (or sth else from Systems Biology)

2. Time constrains: maybe divide last semester into 2: first part for one of the projects above or sth Hugh will come up with.
    Second part for polishing one of those 3 projects.

3. Possible improvements for my Motifs+LibSVM package:
    a) random selection of sequences to test/training set
    b) suffix trees to enable any number of mismatches
    c) regex as a pattern for motif to find
    d) implement 10-fold cross-validation (now, it's only inside libsvm to validate parameters for kernel)
