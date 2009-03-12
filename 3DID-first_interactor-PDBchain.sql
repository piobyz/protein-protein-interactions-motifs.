.output 3DID-first_interactor-PDBchain.out
SELECT p1.name, p1.chain
FROM PDB as p1, Interacting_PDBs as i1, PDB as p2, Interacting_PDBs as i2
WHERE p1.id = i1.PDB_first_id
AND p2.id = i2.PDB_second_id
AND i1.id = i2.id;
