-- Base optionnelle PostgreSQL/PostGIS, uniquement données de démonstration.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS parcels (
 parcel_id TEXT PRIMARY KEY, district TEXT, land_area_m2 NUMERIC,
 zoning TEXT, owner_type TEXT, land_value_eur NUMERIC, last_review DATE
);
CREATE TABLE IF NOT EXISTS assets (
 row_id BIGSERIAL PRIMARY KEY, asset_id TEXT, name TEXT, category TEXT,
 status TEXT, district TEXT, address TEXT, parcel_ref TEXT,
 surface_m2 NUMERIC, built_year INTEGER, occupancy_pct NUMERIC,
 latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
 energy_rating TEXT, annual_cost_eur NUMERIC, estimated_value_eur NUMERIC,
 last_inspection DATE, manager_service TEXT, floor_count INTEGER
);
CREATE TABLE IF NOT EXISTS inspections (
 inspection_id TEXT PRIMARY KEY, asset_id TEXT, inspection_date DATE,
 inspection_type TEXT, result TEXT, estimated_work_eur NUMERIC
);
CREATE TABLE IF NOT EXISTS works (
 work_id TEXT PRIMARY KEY, asset_id TEXT, work_type TEXT,
 budget_eur NUMERIC, progress_pct NUMERIC, status TEXT
);
CREATE INDEX IF NOT EXISTS idx_assets_district ON assets(district);
CREATE INDEX IF NOT EXISTS idx_assets_parcel ON assets(parcel_ref);
CREATE INDEX IF NOT EXISTS idx_assets_geom ON assets USING gist (ST_SetSRID(ST_MakePoint(longitude,latitude),4326)) WHERE latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180;
