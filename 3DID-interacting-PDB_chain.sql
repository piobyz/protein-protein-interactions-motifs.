-- sqlite3 3did_simple.db < ../PPIM/3DID-interacting-PDB_chain.sql
-- .output 3DID-all-interacting-PDB_chain_seq.out
SELECT p1.name, p1.chain, p2.name, p2.chain, i1.joined_interface_seq
FROM PDB as p1, Interacting_PDBs as i1, PDB as p2, Interacting_PDBs as i2
WHERE p1.id = i1.PDB_first_id
AND p2.id = i2.PDB_second_id
AND i1.id = i2.id;
