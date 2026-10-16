import pandas as pd
from src.quality import detect_anomalies,quality_summary,validate_schema
from src.data_access import load_assets

def test_demo_has_anomalies():
    issues=detect_anomalies(load_assets())
    assert len(issues)>0
    assert 'ID dupliqué' in issues['rule'].values
    assert 'Surface invalide' in issues['rule'].values

def test_clean_record():
    df=load_assets().iloc[[0]].copy()
    df['asset_id']='UNIQUE-999'
    df['surface_m2']=150
    df['occupancy_pct']=55
    df['built_year']=2000
    df['latitude']=43.61
    df['longitude']=3.87
    assert len(detect_anomalies(df))==0

def test_score_bounds():
    df=load_assets()
    m=quality_summary(df,detect_anomalies(df))
    assert 0<=m['conformity_pct']<=100
    assert m['records']==len(df)

def test_schema_error():
    try: validate_schema(pd.DataFrame({'asset_id':['X']}))
    except ValueError: pass
    else: assert False,'A missing column must trigger ValueError'
