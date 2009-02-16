SELECT Interactions.id AS interaction,
    Interactions.interactor_one AS interactor_one, PDB_UniProt.pdb AS pdb_one, PDB_UniProt.chain AS chain_one,
    Interactions.interactor_two AS interactor_two, PDB_UniProt.pdb AS pdb_two, PDB_UniProt.chain AS chain_two
FROM Interactions, PDB_UniProt, Interactors, Structures
-- interactor_one
WHERE interactor_one IN(
    SELECT DISTINCT Structures.interactor_id
    FROM Structures)
AND (SELECT Structures.interactor_id, Structures.PDB_UniProt_id AS corresponding_pdb
    FROM Structures
    WHERE Structures.interactor_id = interactor_one)
AND PDB_UniProt.id = corresponding_pdb
-- interactor_two
AND interactor_two IN(
    SELECT DISTINCT Structures.interactor_id
    FROM Structures)
AND (SELECT Structures.interactor_id, Structures.PDB_UniProt_id AS corresponding_pdb
    FROM Structures
    WHERE Structures.interactor_id = interactor_two)
AND PDB_UniProt.id = corresponding_pdb;