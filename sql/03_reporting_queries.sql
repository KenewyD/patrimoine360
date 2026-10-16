-- Nombre de biens et surface déclarée par secteur
SELECT district, COUNT(*) AS nombre_biens,
 SUM(CASE WHEN surface_m2 > 0 THEN surface_m2 ELSE 0 END) AS surface_valide_m2
FROM assets GROUP BY district ORDER BY nombre_biens DESC;

-- Synthèse par usage
SELECT category, COUNT(*) AS nombre_biens,
 ROUND(AVG(CASE WHEN occupancy_pct BETWEEN 0 AND 100 THEN occupancy_pct END),1) AS occupation_moyenne
FROM assets GROUP BY category ORDER BY nombre_biens DESC;

-- Extension PostGIS facultative (après CREATE EXTENSION postgis)
-- SELECT asset_id, ST_SetSRID(ST_MakePoint(longitude, latitude),4326) AS geom
-- FROM assets WHERE longitude IS NOT NULL AND latitude IS NOT NULL;
