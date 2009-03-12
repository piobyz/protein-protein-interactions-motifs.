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

\*.db files were prepared by DIP.py and DBDIP.py

TODO: note that input files need to be corrected manually in source before every run.

TODO: automate whole workflow!!

TODO: automate launching SQL scripts / write them using SQLAlchemy

TODO: logging all the intermediate and final results (stats + were the output files were written)

TODO compare_pdb_list.py see TODOs inside the file

TODO !!! check whether there are some issue with case sensitive PDB IDs in every file I use !!!


Workflow:
1. assume we have downloaded mif files from DIP for every species

2. sqlite3 DIP-Ecoli.db < ../PPIM/DIP-both_interacting-detailed.sql (change .output inside the sql file)

3. now we have PDB1|chain1|PDB2|chain2 for every species in \*.output files

4. run once: sqlite3 3did_simple.db < ../PPIM/3DID-interacting-PDB_chain.sql (produces 3DID-all-interacting-PDB_chain_seq.out)

5. python DIP-both_interacting-reverse.py ../DB/Interacting_PDBs-DIP-in-3DID/Ecoli.output

6. Now, we have Ecoli.output-reversed-without-duplicates.out-overlapping-3DID.fa with overlapping PDBs in \*.fa file ready for SVM

7. In order to compare overlapping PDBs (without chains) from *the same species* in DIP, 3DID and JENA:

- prepare file with PDBs from DIP: DIP-single_line-PDB.sql (change .output and concatenate PDB1 and PDB2!!)

- prepare 3DID (once only): 3DID-first_interactor-PDBchain.sql

- (change .output and make sure that p1.name and p2.name are run and then cat output1 output2 > final.output are concatenated)

8. JENA single line PDBs are prepared manually copying PDBs directly from their site and extracting PDB IDs, results stored in /JENA

9. Finally, run compare_pdb_list.py (see TODO above...) with DIP vs 3DID, DIP vs JENA, JENA vs 3DID


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
