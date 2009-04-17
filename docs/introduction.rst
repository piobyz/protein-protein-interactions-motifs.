============
Introduction
============

Simon, Baldo and Richard's dataset
**********************************

Motivation and Approach
-----------------------
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

.. image:: ../doc/DB_schema.pdf
   :height: 100
   :width: 200
   :scale: 50

DB mapping and parsing workflow are in DB.py and PPIMotifs.py, respectively.
SQL query used to find distinctive patches: Distinct_patches_307.sql

Results
-------
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


DIP with 3DID
*************

Motivation and Approach
-----------------------
DIP has datasets with interactions grouped by species (MIF 2.5 format, 
http://dip.doe-mbi.ucla.edu/dip/Download.cgi?SM=7)
Provided XML files have DIP ID for interactors and interactions and, among others, UniProt IDs
which were mapped to the corresponding PDB|chain using mapping from
http://www.bioinf.org.uk/pdbsws/pdbsws_chain.txt
Database's schema is in file: DIP_schema, DB's files are in: DB/DIP-species/\*.db

.. image:: ../doc/DIP_schema.pdf
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

.. image:: ../doc/3DID_schema.pdf
   :height: 100
   :width: 200
   :scale: 50

For each species (from each \*.db file) there were files with PDB1|chain1|PDB2|chain2 interactions prepared.
Subsequently, the content of file above was compared against all interactions from 3DID and corresponding interactions were saved
together with corresponding sequence.

In order to check how similar all the 3DID sequences are we used PISCES service, which given some cutoff returns
a subset of all provided PDB|chain where sequence percentage identity is less or equal to cutoff %.

 *http://dunbrack.fccc.edu/Guoli/PISCES.php*


* For **90% cutoff** PISCES returned *10 373* out of 110 594 (~ **9.5%** ).
* For **75% cutoff** *9 343* (~ **8.5%** ) structures were returned (out of 110 594).

Because mapping from DIP to 3DID interactions were very poor we wanted to verify those results.
Jena Library was used, which among others, provides mapping from PDB identifiers to species.

 *http://www.fli-leibniz.de/IMAGE.html*


Results
-------
Results for this approach are extensively described in section "Results".

IMEx
****
To investigate. Seems that this is going to be a standard in describing PPI (DIP, IntAct, others)
XML is v. hard to read, but all necessary infos should be there.

Not many interactions included yet (about 1000, human curated (from literature)
and those sent by researchers together with publication).

Also, see e-mail from Lukasz Salwinski.

SCOPPI
******
Looks good (i.e. rendered images with interface exposed) but does not provide any flat files.

PIBASE
******
Looks OK, got flat files with interactions and sequences involved.
Also, see e-mail from Fred Davis describing columns in flat files.

STRING
******
Nice looking, but no information about directly interacting domains / interfaces / sequences.

"Cataloging the Relationships..." review paper
**********************************************


IntAct, MINT, BIND, others?
***************************

MODBASE, iPfam
**************


Acknowledge
***********
I would like to thank Anna Gajda for bio-related discussions we had.

I would like to thank Bartek Bargiel for his continuos help in my numerous programming-related issues during development of this package.

I would like to thank Python Community for creating excellent tools used during development of this package (Python language itself, SQLAlchemy, Nose, Sphinx).

I would like to thank authors of databases DIP and 3DID for work they have done and always quick and detailed answers to questions I had.
