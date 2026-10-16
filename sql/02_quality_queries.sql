-- Détecter les identifiants dupliqués
SELECT asset_id, COUNT(*) AS occurrences
FROM assets GROUP BY asset_id HAVING COUNT(*) > 1;

-- Surfaces invalides ou données obligatoires manquantes
SELECT asset_id, district, surface_m2, parcel_ref
FROM assets
WHERE surface_m2 IS NULL OR surface_m2 <= 0 OR parcel_ref IS NULL OR TRIM(parcel_ref)='';

-- Années de construction à contrôler
SELECT asset_id, built_year FROM assets
WHERE built_year IS NOT NULL AND (built_year < 1800 OR built_year > 2026);

-- Taux d'occupation incohérents
SELECT asset_id, occupancy_pct FROM assets
WHERE occupancy_pct IS NOT NULL AND (occupancy_pct < 0 OR occupancy_pct > 100);
