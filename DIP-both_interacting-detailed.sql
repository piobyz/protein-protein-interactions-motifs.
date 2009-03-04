-- .output Hsapi.output
SELECT 
    PDB1.pdb, PDB1.chain,
    PDB2.pdb, PDB2.chain
FROM Interactions,
    Interactors AS Int1, Interactors AS Int2,
    Structures AS Str1, Structures AS Str2,
    PDB_UniProt AS PDB1, PDB_UniProt AS PDB2
WHERE (
    (Interactions.interactor_one=Int1.id)
    AND (Int1.id=Str1.interactor_id)
    AND (Str1.PDB_Uniprot_id=PDB1.id)
) 
AND (
    (Interactions.interactor_two=Int2.id)
    AND (Int2.id=Str2.interactor_id)
    AND (Str2.PDB_Uniprot_id=PDB2.id)
)
GROUP BY Interactions.interactor_one, Interactions.interactor_two;