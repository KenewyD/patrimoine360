-- Audit des références orphelines
SELECT a.asset_id,a.parcel_ref FROM assets a
LEFT JOIN parcels p ON a.parcel_ref=p.parcel_id
WHERE a.parcel_ref IS NOT NULL AND p.parcel_id IS NULL;
-- Doublons d'identifiants métier (volontairement non contraints dans cet échantillon sale)
SELECT asset_id,COUNT(*) AS occurrences FROM assets
GROUP BY asset_id HAVING COUNT(*)>1 ORDER BY occurrences DESC;
-- KPI surfaces par secteur, hors valeurs incorrectes
SELECT district,COUNT(*) AS nb_biens,
 ROUND(SUM(CASE WHEN surface_m2>0 THEN surface_m2 ELSE 0 END),0) AS surface_valide_m2,
 ROUND(AVG(CASE WHEN occupancy_pct BETWEEN 0 AND 100 THEN occupancy_pct END),1) AS occupation_moyenne
FROM assets GROUP BY district ORDER BY nb_biens DESC;
-- Spatial illustration, points non officiels
SELECT asset_id, ST_AsText(ST_SetSRID(ST_MakePoint(longitude,latitude),4326)) AS geom
FROM assets WHERE latitude BETWEEN 43.4 AND 43.9 AND longitude BETWEEN 3.5 AND 4.2;
