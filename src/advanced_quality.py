"""Extended synthetic property quality checks. Never modifies source records."""
import pandas as pd

FIELDS=['asset_id','name','category','status','district','address','parcel_ref','surface_m2','built_year','occupancy_pct','latitude','longitude','energy_rating','annual_cost_eur','estimated_value_eur','last_inspection','manager_service','floor_count']
VALID_CATEGORIES={'Bureau','École','Équipement sportif','Centre culturel','Dépôt','Local associatif','Bâtiment technique','Parking'}
VALID_STATUS={'Actif','En travaux','Vacant','Cédé'}

def audit_assets(df, parcels=None):
    absent=set(FIELDS)-set(df.columns)
    if absent: raise ValueError(f'Colonnes manquantes: {sorted(absent)}')
    out=[]
    pids=set(parcels['parcel_id'].dropna().astype(str)) if parcels is not None else None
    ids=df['asset_id'].astype('string').str.strip()
    dup=ids.notna() & ids.ne('') & ids.duplicated(keep=False)
    def add(i,identifier,rule,severity,field,detail):
        out.append({'row_number':i+1,'asset_id':identifier,'rule':rule,'severity':severity,'field':field,'detail':detail,'status':'À traiter'})
    for i,(_,v) in enumerate(df.iterrows()):
        asset=str(v['asset_id']) if pd.notna(v['asset_id']) else f'ligne-{i+1}'
        if pd.isna(v['asset_id']) or not str(v['asset_id']).strip(): add(i,asset,'Identifiant absent','Critique','asset_id','ID requis')
        if dup.iloc[i]:add(i,asset,'Identifiant dupliqué','Critique','asset_id','Unicité violée')
        for f in ['name','district','address','parcel_ref','manager_service']:
            if pd.isna(v[f]) or not str(v[f]).strip():add(i,asset,'Champ obligatoire vide','Élevée',f,'Valeur absente')
        if pd.notna(v['category']) and v['category'] not in VALID_CATEGORIES:add(i,asset,'Catégorie inconnue','Moyenne','category','Valeur hors référentiel')
        if pd.notna(v['status']) and v['status'] not in VALID_STATUS:add(i,asset,'Statut inconnu','Moyenne','status','Valeur hors référentiel')
        if pids is not None and pd.notna(v['parcel_ref']) and str(v['parcel_ref']) not in pids:add(i,asset,'Référence cadastrale orpheline','Élevée','parcel_ref','Parcelle absente du référentiel fictif')
        numeric=[('surface_m2','Surface invalide','Élevée',lambda a:a<=0),('occupancy_pct','Occupation hors bornes','Élevée',lambda a:a<0 or a>100),('annual_cost_eur','Coût annuel négatif','Moyenne',lambda a:a<0),('estimated_value_eur','Valeur estimée négative','Élevée',lambda a:a<0),('floor_count','Étages invalides','Moyenne',lambda a:a<=0)]
        for field,rule,sev,pred in numeric:
            val=pd.to_numeric(v[field],errors='coerce')
            if pd.isna(val):add(i,asset,'Numérique absent','Moyenne',field,'Valeur manquante ou non numérique')
            elif pred(val):add(i,asset,rule,sev,field,f'Valeur: {val}')
        year=pd.to_numeric(v['built_year'],errors='coerce')
        if pd.isna(year) or not 1800<=year<=2026:add(i,asset,'Année construction incohérente','Moyenne','built_year','Plage attendue 1800–2026')
        if pd.isna(v['energy_rating']) or str(v['energy_rating']) not in list('ABCDEFG'):add(i,asset,'Classe énergie invalide','Moyenne','energy_rating','Valeurs A à G')
        lat=pd.to_numeric(v['latitude'],errors='coerce');lon=pd.to_numeric(v['longitude'],errors='coerce')
        if pd.isna(lat) or pd.isna(lon) or not (43.4<=lat<=43.9 and 3.5<=lon<=4.2):add(i,asset,'Géolocalisation incohérente','Élevée','latitude/longitude','Hors zone illustrative ou absent')
        if pd.isna(v['last_inspection']):add(i,asset,'Inspection non renseignée','Moyenne','last_inspection','Date absente')
        elif pd.to_datetime(v['last_inspection'],errors='coerce') is pd.NaT:add(i,asset,'Date inspection incorrecte','Moyenne','last_inspection','Date invalide')
        if v['status']=='Vacant' and pd.notna(v['occupancy_pct']) and pd.to_numeric(v['occupancy_pct'],errors='coerce')>0:add(i,asset,'Vacance / occupation contradictoire','Élevée','status/occupancy_pct','Bien vacant et occupé')
    return pd.DataFrame(out,columns=['row_number','asset_id','rule','severity','field','detail','status'])

def summarize_audit(df, issues):
    n=len(df); flagged=issues.row_number.nunique() if len(issues) else 0
    return {'records':n,'flagged_records':int(flagged),'anomalies':len(issues),'conformity_pct':round(100*(n-flagged)/n,1) if n else 100.0}
