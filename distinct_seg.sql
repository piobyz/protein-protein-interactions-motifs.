SELECT COUNT(DISTINCT Patches_seed.sequence)
FROM Patches_seed, Proteins_seed, Homologues, Proteins_putative, Interactions
WHERE (Patches_seed.length>2)
AND (Proteins_seed.name=Interactions.seed_reaction)
AND (
    (Proteins_seed.id=Homologues.protein_seed_id)
    AND (Homologues.protein_putative_id=Proteins_putative.id)
)
AND (
    (Proteins_putative.name=Interactions.first_protein_putative_id)
    OR (Proteins_putative.name=Interactions.second_protein_putative_id)
);