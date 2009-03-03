SELECT COUNT(p1.id)
FROM PDB as p1, Interacting_PDBs as i1, PDB as p2, Interacting_PDBs as i2
WHERE p1.id = i1.PDB_first_id
AND p2.id = i2.PDB_second_id
GROUP BY p1.id, p2.id;
