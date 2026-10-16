import pandas as pd
from src.decision import rank_interventions,allocate_budget

def test_priority_budget():
    a=pd.DataFrame([dict(asset_id='A',energy_rating='G',occupancy_pct=90,surface_m2=200,annual_cost_eur=5000),dict(asset_id='B',energy_rating='A',occupancy_pct=10,surface_m2=300,annual_cost_eur=1000)])
    i=pd.DataFrame([dict(asset_id='A',result='Non conforme'),dict(asset_id='B',result='Conforme')])
    w=pd.DataFrame([dict(asset_id='A',budget_eur=20000)])
    ranked=rank_interventions(a,i,w)
    assert ranked.iloc[0].asset_id=='A'
    chosen,remaining=allocate_budget(ranked,20000)
    assert chosen.asset_id.tolist()==['A'] and remaining==0

def test_zero_budget():
    a=pd.DataFrame([dict(asset_id='A',energy_rating='A',occupancy_pct=20,surface_m2=200,annual_cost_eur=20)])
    ranked=rank_interventions(a,pd.DataFrame(columns=['asset_id','result']),pd.DataFrame(columns=['asset_id','budget_eur']))
    assert len(allocate_budget(ranked,0)[0])==0
