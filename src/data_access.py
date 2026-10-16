from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
def load_assets(): return pd.read_csv(BASE/'data'/'assets_synthetic.csv',low_memory=False)
def load_parcels(): return pd.read_csv(BASE/'data'/'parcels_synthetic.csv')
def load_inspections(): return pd.read_csv(BASE/'data'/'inspections_synthetic.csv')
def load_works(): return pd.read_csv(BASE/'data'/'works_synthetic.csv')
