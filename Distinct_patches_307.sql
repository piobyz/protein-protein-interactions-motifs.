SELECT COUNT(DISTINCT Patches_seed.sequence)
FROM Patches_seed
WHERE Patches_seed.protein_seed_id
IN(
    SELECT DISTINCT Proteins_seed.id
    FROM Proteins_seed
    WHERE EXISTS(
        SELECT seed_reaction
        FROM Interactions
        WHERE Interactions.seed_reaction = Proteins_seed.name)
)
AND Patches_seed.length>2;