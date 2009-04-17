==========
Discussion
==========

Where to look for a data?
*************************

From the beginning of this project we struggled to find data source containing all necessary data.
What we needed was sequence data from the interface of both interacting proteins (called interface).
There are numerous databases containing PPI data but as described in introduction almost all of them lack of some crucial to us data.

After finally combining two sources of information (DIP and 3DID) we encountered very small number of high-quality examples to train our SVM classifier.
Why DIP? Because it is curated database were interaction were proven experimentally. It might be seen as the gold standard in PPI.
What's more it's divided into species allowing to combine those data with other sources specific to a particular species.

Why 3DID? Because it consists of interfaces -- recognized parts of the proteins involved in specific binding taking place between proteins when they are interacting.
Interfaces are bound to already resolved 3D structures from PDB so it's also a well proven evidence of interaction.

DIP without 3DID lacks of interface sequence data.
3DID without DIP lack of verification (??)

As shown in results section overlapping interaction are very rare. In fact, too rare to efficiently train SVM classifier.

There are many sources of PPI but I tried to avoid the possible noise by avoiding many overloaded sources where interactions are easily accepted.
This would be probably enough for the classifier but results would be most likely not valuable.



String Kernels in PPI classification
************************************

Firstly, results using String Kernels (SK) were rather unsatisfactory.
Detailed results are presented only for the top interacting pair of domains (PUT PFAM IDS HERE).
I used String Kernel of length 3 without any mismatches and allowing one mismatch.
(EXPLAIN HOW COMPUTATIONALLY EXPENSIVE IT IS TO CALCULATE ANYTHING ABOVE 5-MER)
Kernels were linear and radial basis.
Three different sizes of training set were used (25, 50 and 75%).

To verify those data I run basic identity check.
It performed much better than SK.
Some basic statistics are included in the end of results section.

