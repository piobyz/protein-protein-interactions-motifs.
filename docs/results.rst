Results
=======

TODO: logging all the intermediate and final results (stats + were the output files were written)

TODO: Create nice looking report from logged results + documentation / doctests using Sphinx

TODO: create setup.py (see: http://github.com/ctb/pygr/blob/4a3f16fbab1647b8da15c8ab1b930654de8f8e01/setup.py)

TODO: !!! check whether there are some issue with case sensitive PDB IDs in every file I use


Workflow above were applied to all species from DIP and overlapping PDB|chain are very rare.
For example: M.Musculus **7** overlapping PDB|chain, H.Sapiens - **31**. There were **93** interactions
from DIP concerning mouse, and **718** concerning human. Reversed interactions were also included
(pdb1|chain1 <->pdb2|chain2 -> pdb2|chain2 <-> pdb1|chain1 ; <-> meaning 'interacts with')
in comparisons. Total number of 3DID interactions were **99160**.

C.elegans
*********

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 0   |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 4   |
+-------------------------------+-----+
| DIP - JENA                    | 5   |
+-------------------------------+-----+
| JENA - 3DID                   | 43  |
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 5     |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 98    |
+-------------------------+-------+


D.melanogaster
**************

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 4   |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 16  |
+-------------------------------+-----+
| DIP - JENA                    | 20  |
+-------------------------------+-----+
| JENA - 3DID                   | 171 |
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 30    |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 337   |
+-------------------------+-------+

E.coli
******

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 14  |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 115 |
+-------------------------------+-----+
| DIP - JENA                    | 163 |
+-------------------------------+-----+
| JENA - 3DID                   | 2807|
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 169   |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 4847  |
+-------------------------+-------+

H.pylori
********

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 0   |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 4   |
+-------------------------------+-----+
| DIP - JENA                    | 5   |
+-------------------------------+-----+
| JENA - 3DID                   | 102 |
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 6     |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 165   |
+-------------------------+-------+


H.sapiens
*********

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 31  |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 4   |
+-------------------------------+-----+
| DIP - JENA                    | 5   |
+-------------------------------+-----+
| JENA - 3DID                   | 102 |
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 6     |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 165   |
+-------------------------+-------+


M.musculus
**********

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 7   |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 75  |
+-------------------------------+-----+
| DIP - JENA                    | 78  |
+-------------------------------+-----+
| JENA - 3DID                   | 1499|
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 125   |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 2557  |
+-------------------------+-------+

S.cerevisiae
************

Number of overlapping entries:

+-------------------------------+-----+
| DIP - 3DID interactions       | 56  |
+-------------------------------+-----+
|Overlapping PDB IDs DIP - 3DID | 201 |
+-------------------------------+-----+
| DIP - JENA                    | 341 |
+-------------------------------+-----+
| JENA - 3DID                   | 809 |
+-------------------------------+-----+


Sizes of data sets:

+-------------------------+-------+
| Distinct DIP set size   | 359   |
+-------------------------+-------+
|Distinct 3DID set size   | 27132 |
+-------------------------+-------+
| Distinct JENA set size  | 1610  |
+-------------------------+-------+

S.cerevisiae 25% (3,0), (3,1), (4,0), (4,1) (shuffling sequence as in TFBS project)
***********************************************************************************
(Run on 11.03, 7 hours)

TRAINING +: 42 TRAINING -: 42

TEST +: 7 TEST -: 7

25 % training set


#. (3,0): Training: extras/svm-train -c 0.03125 -g 0.0001220703125 
#. (3,1): Training: extras/svm-train -c 0.03125 -g 0.0001220703125 
#. (4,0): Training: extras/svm-train -c 0.03125 -g 0.0001220703125 
#. (4,1): Training: extras/svm-train -c 0.03125 -g 0.0001220703125 

+----------------------+----------------------+
|                      |        Accuracy      |
+----------------------+----------------------+
| Radial Kernel (3, 0) | 71.4286% (10/14)     |
+----------------------+----------------------+
| Linear Kernel (3, 0) | 64.2857% (9/14)      |
+----------------------+----------------------+
| Radial Kernel (3, 1) | 85.7143% (12/14)     |
+----------------------+----------------------+
| Linear Kernel (3, 1) | 57.1429% (8/14)      |
+----------------------+----------------------+
| Radial Kernel (4, 0) | 42.8571% (6/14)      |
+----------------------+----------------------+
| Linear Kernel (4, 0) | 21.4286%             |
+----------------------+----------------------+
| Radial Kernel (4, 1) | 64.2857% (9/14)      |
+----------------------+----------------------+
| Linear Kernel (4, 1) | 42.8571% (6/14)      |
+----------------------+----------------------+


Most interactions classifier 50% (3,0), (3,1), (shuffling sequence as in TFBS project)
**************************************************************************************
(Run on 16.03, 9 hours)

TRAINING +: 940 TRAINING -: 940

TEST +: 469 TEST -: 470

50 % training set

#. (3,0): extras/svm-train -c 0.03125 -g 0.0001220703125
#. (3,1): extras/svm-train -c 0.03125 -g 0.0001220703125

+----------------------+----------------------+
|                      |        Accuracy      |
+----------------------+----------------------+
| Radial Kernel (3, 0) | 47.1778% (443/939)   |
+----------------------+----------------------+
| Linear Kernel (3, 0) | 58.7859% (552/939)   |
+----------------------+----------------------+
| Radial Kernel (3, 1) | 48.7753% (458/939)   |
+----------------------+----------------------+
| Linear Kernel (3, 1) | 63.6848% (598/939)   |
+----------------------+----------------------+

Number of interactions (from 3DID) per pair of domains (in Pfam format) 
***********************************************************************
+-------+---------+-----+
|PF02800| PF00044 | 624 |
+-------+---------+-----+
|PF00036| PF00036 | 779 |
+-------+---------+-----+
|PF00139| PF00139 | 784 |
+-------+---------+-----+
|PF07654| PF00129 | 828 |
+-------+---------+-----+
|PF00043| PF02798 | 875 |
+-------+---------+-----+
|PF00210| PF00210 | 1422|
+-------+---------+-----+
|PF07654| PF07686 | 1520|
+-------+---------+-----+
|PF00227| PF00227 | 1808|
+-------+---------+-----+
|PF07686| PF07686 | 1848|
+-------+---------+-----+
|PF07654| PF07654 | 1879|
+-------+---------+-----+

Results for top pair of domain interactions (after random pairs choice implementation)
**************************************************************************************

25 % training set
-----------------

(Run on 14.04, 49 hours)

TRAINING + 1410 TRAINING - 1410

TEST + 469 TEST - 469

#. (3,0): Training: extras/svm-train -c 8.0 -g 0.03125
#. (3,1): Training: extras/svm-train -c 8.0 -g 0.03125 

+----------------------+----------------------+
|                      |        Accuracy      |
+----------------------+----------------------+
| Radial Kernel (3, 0) | 50% (469/938)        |
+----------------------+----------------------+
| Linear Kernel (3, 0) | 74.5203% (699/938)   |
+----------------------+----------------------+
| Radial Kernel (3, 1) | 50% (469/938)        |
+----------------------+----------------------+
| Linear Kernel (3, 1) | 62.58% (587/938)     |
+----------------------+----------------------+

50 % training set
-----------------

(Run on 23.03, 9 hours)

TRAINING + 940 TRAINING - 940

TEST + 939 TEST - 939

#. (3,0): Training: extras/svm-train -c 2.0 -g 0.03125
#. (3,1): Training: extras/svm-train -c 2.0 -g 0.03125 

+----------------------+----------------------+
|                      |        Accuracy      |
+----------------------+----------------------+
| Radial Kernel (3, 0) | 50% (939/1878)       |
+----------------------+----------------------+
| Linear Kernel (3, 0) | 72.6837% (1365/1878) |
+----------------------+----------------------+
| Radial Kernel (3, 1) | 50% (939/1878)       |
+----------------------+----------------------+
| Linear Kernel (3, 1) | 61.1289% (1148/1878) |
+----------------------+----------------------+


75 % training set
-----------------

(Run on 14.04, 6 hours)

TRAINING + 470 TRAINING - 470

TEST + 1409 TEST - 1409

#. (3,0): Training: extras/svm-train -c 8.0 -g 0.03125
#. (3,1): Training: extras/svm-train -c 8.0 -g 0.03125 

+----------------------+----------------------+
|                      |        Accuracy      |
+----------------------+----------------------+
| Radial Kernel (3, 0) | 50% (1409/2818)      |
+----------------------+----------------------+
| Linear Kernel (3, 0) | 71.3627% (2011/2818) |
+----------------------+----------------------+
| Radial Kernel (3, 1) | 50% (1409/2818)      |
+----------------------+----------------------+
| Linear Kernel (3, 1) | 57.9844% (1634/2818) |
+----------------------+----------------------+

Identity results (for top domains interactions pair)
****************************************************

24.03 11:33 - 29.03 5:17, running time: 4 days, 17 hours


Dividing data/most_interacting_domain_pairs_interfaces.fa into TEST +: 939, TRAINING +: 940

938 observations summary::

 Min.   :23.50  
 1st Qu.:79.45  
 Median :87.15  
 Mean   :83.31  
 3rd Qu.:92.50  
 Max.   :98.70
 