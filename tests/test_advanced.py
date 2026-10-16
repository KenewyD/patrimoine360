import pandas as pd
from src.data_access import load_assets,load_parcels,load_inspections,load_works
from src.advanced_quality import audit_assets,summarize_audit

def test_large_datasets():
    assert len(load_assets())==6500
    assert len(load_parcels())==3200
    assert len(load_inspections())==12500
    assert len(load_works())==1800

def test_advanced_anomalies():
    issues=audit_assets(load_assets(),load_parcels())
    assert len(issues)>100
    assert issues.rule.nunique()>=12
    assert 'Référence cadastrale orpheline' in set(issues.rule)

def test_summary_bounds():
    a=load_assets();s=summarize_audit(a,audit_assets(a,load_parcels()))
    assert 0<=s['conformity_pct']<=100

def test_invalid_schema():
    try: audit_assets(pd.DataFrame({'asset_id':['A']}))
    except ValueError: return
    raise AssertionError('Missing columns should fail')
