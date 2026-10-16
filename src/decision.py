"""Transparent rule-based illustrative works prioritization; not a municipal decision engine."""
import pandas as pd

WEIGHTS={'energy':0.30,'condition':0.30,'occupancy':0.20,'cost':0.20}

def rank_interventions(assets, inspections, works):
    """Return unique assets with a reproducible 0-100 priority score and estimated works budget."""
    a=assets.copy()
    a['asset_id']=a['asset_id'].astype(str)
    a=a.drop_duplicates('asset_id',keep='first')
    latest=inspections.copy()
    order={'Conforme':0,'À surveiller':55,'Non conforme':100}
    latest['condition']=latest['result'].map(order).fillna(35)
    condition=latest.groupby('asset_id')['condition'].max()
    cost=works.groupby('asset_id')['budget_eur'].sum()
    a['condition_score']=a.asset_id.map(condition).fillna(35)
    a['energy_score']=a.energy_rating.map(dict(zip(list('ABCDEFG'),[0,15,30,45,60,80,100]))).fillna(50)
    occ=pd.to_numeric(a.occupancy_pct,errors='coerce').fillna(50).clip(0,100)
    a['occupancy_score']=occ
    area=pd.to_numeric(a.surface_m2,errors='coerce').clip(lower=0).fillna(250)
    a['simulated_budget_eur']=(area*150).clip(lower=15000,upper=850000).round(0)
    # Known work budgets take precedence when present.
    a['simulated_budget_eur']=a.asset_id.map(cost).combine_first(a.simulated_budget_eur).clip(lower=0)
    annual=pd.to_numeric(a.annual_cost_eur,errors='coerce').clip(lower=0).fillna(0)
    a['cost_score']=(annual/150000*100).clip(0,100)
    a['priority_score']=(a.energy_score*WEIGHTS['energy']+a.condition_score*WEIGHTS['condition']+a.occupancy_score*WEIGHTS['occupancy']+a.cost_score*WEIGHTS['cost']).round(1)
    a['priority_level']=pd.cut(a.priority_score,bins=[-0.1,35,65,100],labels=['Basse','Modérée','Haute'])
    return a.sort_values(['priority_score','asset_id'],ascending=[False,True])

def allocate_budget(ranked,budget):
    """Select ranked projects until budget exhausted, without splitting projects."""
    remaining=max(0,float(budget)); chosen=[]
    for rec in ranked.itertuples(index=False):
        amount=float(rec.simulated_budget_eur)
        if amount<=remaining:
            chosen.append(rec.asset_id);remaining-=amount
    return ranked[ranked.asset_id.isin(chosen)].copy(),remaining
