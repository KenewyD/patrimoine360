"""Contrôles reproductibles sur des données synthétiques de patrimoine."""
import pandas as pd

REQUIRED = ['asset_id','name','category','status','district','address','parcel_ref','surface_m2','built_year','occupancy_pct','latitude','longitude']

def validate_schema(df):
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Colonnes manquantes : {', '.join(missing)}")

def detect_anomalies(df):
    validate_schema(df)
    findings = []
    ids = df['asset_id'].astype('string').str.strip()
    counts = ids[ids.notna() & ids.ne('')].value_counts()
    for idx, r in df.iterrows():
        ident = str(r['asset_id']) if pd.notna(r['asset_id']) else f'ligne-{idx+1}'
        def add(rule,severity,detail):
            findings.append({'row_number':idx+1,'asset_id':ident,'rule':rule,'severity':severity,'detail':detail})
        if pd.isna(r['asset_id']) or not str(r['asset_id']).strip(): add('ID manquant','Critique','Identifiant absent')
        elif counts.get(str(r['asset_id']).strip(),0)>1: add('ID dupliqué','Critique','Identifiant utilisé plusieurs fois')
        for key in ('name','district','address','parcel_ref'):
            if pd.isna(r[key]) or not str(r[key]).strip(): add('Champ obligatoire absent','Élevée',f'{key} absent')
        area = pd.to_numeric(r['surface_m2'],errors='coerce')
        if pd.isna(area) or area <= 0: add('Surface invalide','Élevée','Surface nulle, négative ou manquante')
        yr = pd.to_numeric(r['built_year'],errors='coerce')
        if pd.notna(yr) and (yr<1800 or yr>2026): add('Année incohérente','Moyenne','Année de construction hors plage')
        occupancy = pd.to_numeric(r['occupancy_pct'],errors='coerce')
        if pd.notna(occupancy) and not 0 <= occupancy <= 100: add('Occupation invalide','Élevée','Taux hors 0–100 %')
        lat = pd.to_numeric(r['latitude'],errors='coerce');lon=pd.to_numeric(r['longitude'],errors='coerce')
        if pd.isna(lat) or pd.isna(lon) or not (43.4<=lat<=43.9 and 3.5<=lon<=4.2): add('Coordonnées à vérifier','Moyenne','Coordonnées absentes ou hors zone de démonstration')
    return pd.DataFrame(findings,columns=['row_number','asset_id','rule','severity','detail'])

def quality_summary(df,findings):
    n=len(df)
    bad_rows=int(findings['row_number'].nunique()) if len(findings) else 0
    return {'records':n,'flagged_records':bad_rows,'anomalies':len(findings),'conformity_pct':round(100*(n-bad_rows)/n,1) if n else 100.0}

def aggregate_by_district(df,findings):
    base=df.copy()
    flagged=set(findings['row_number'].tolist())
    base['has_anomaly']=[i+1 in flagged for i in range(len(base))]
    out=base.groupby('district',dropna=False).agg(buildings=('asset_id','size'),surface_m2=('surface_m2',lambda s:pd.to_numeric(s,errors='coerce').clip(lower=0).sum()),flagged=('has_anomaly','sum')).reset_index()
    return out
