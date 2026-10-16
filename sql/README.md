# Base PostgreSQL/PostGIS optionnelle

Démarrer `docker compose up -d`. Exécuter le schéma puis importer les CSV dans l'ordre : parcels, assets, inspections, works. Sous `psql` :

```sql
\i sql/01_schema.sql
\copy parcels(parcel_id,district,land_area_m2,zoning,owner_type,land_value_eur,last_review) FROM 'data/parcels_synthetic.csv' CSV HEADER
\copy assets(asset_id,name,category,status,district,address,parcel_ref,surface_m2,built_year,occupancy_pct,latitude,longitude,energy_rating,annual_cost_eur,estimated_value_eur,last_inspection,manager_service,floor_count) FROM 'data/assets_synthetic.csv' CSV HEADER
\copy inspections(inspection_id,asset_id,inspection_date,inspection_type,result,estimated_work_eur) FROM 'data/inspections_synthetic.csv' CSV HEADER
\copy works(work_id,asset_id,work_type,budget_eur,progress_pct,status) FROM 'data/works_synthetic.csv' CSV HEADER
```

Chemins `\copy` relatifs à votre dossier courant. Les identifiants de bâtiments ne sont volontairement pas des clés uniques pour permettre d'étudier les doublons. Les références de biens des inspections et travaux peuvent être répétées.
