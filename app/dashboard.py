# Patrimoine Data 360 — independent fictional demonstrator
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_access import load_assets,load_parcels,load_inspections,load_works
from src.advanced_quality import audit_assets,summarize_audit
from src.decision import rank_interventions,allocate_budget

st.set_page_config(page_title='Patrimoine Data 360 | Observatoire',page_icon='🏛️',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.15rem;max-width:1450px}
[data-testid="stSidebar"]{background:#102238}
[data-testid="stSidebar"] *{color:#edf4fb!important}
.hero{background:linear-gradient(108deg,#122c48,#136e83);padding:22px 26px;border-radius:16px;color:white;margin-bottom:16px}
.hero h1{margin:0;font-size:2.05rem;color:white}
.hero p{margin:8px 0 0;color:#d6eef3}
[data-testid="stMetric"]{background:#f1f6f9;padding:14px;border-radius:12px;border:1px solid #dae6eb}
.small-note{font-size:0.86rem;color:#556876}
</style>''',unsafe_allow_html=True)
@st.cache_data(show_spinner='Chargement des données…')
def load():return load_assets(),load_parcels(),load_inspections(),load_works()
@st.cache_data(show_spinner='Audit initial des référentiels…')
def full_audit(a,p):return audit_assets(a,p)
@st.cache_data(show_spinner='Calcul des scénarios…')
def scores(a,i,w):return rank_interventions(a,i,w)
assets_all,parcels,inspections,works=load()
issues_all=full_audit(assets_all,parcels)
priority_all=scores(assets_all,inspections,works)
SECTIONS=['📊 Vue exécutive','🔎 Recherche patrimoniale','🛡️ Centre de qualité','🗺️ Carte SIG','🏗️ Programmation travaux','🧾 Fiche bâtiment','📁 Référentiels & exports','💻 Atelier SQL']
st.sidebar.markdown('### 🏛️ Patrimoine 360')
st.sidebar.caption('Observatoire de démonstration')
page=st.sidebar.radio('ESPACE DE TRAVAIL',SECTIONS,label_visibility='collapsed')
st.sidebar.divider()
st.sidebar.markdown('**Périmètre d’analyse**')
districts=sorted(assets_all.district.dropna().unique())
categories=sorted(assets_all.category.dropna().unique())
selected_districts=st.sidebar.multiselect('Secteurs',districts,default=districts)
selected_categories=st.sidebar.multiselect('Typologies',categories,default=categories)
search=st.sidebar.text_input('Recherche rapide (ID ou nom)',placeholder='BAT-000001')
valid=(assets_all.district.isin(selected_districts)&assets_all.category.isin(selected_categories))
if search.strip():
    valid=valid & (assets_all.asset_id.astype(str).str.contains(search.strip(),case=False,regex=False,na=False)|assets_all.name.astype(str).str.contains(search.strip(),case=False,regex=False,na=False))
a=assets_all.loc[valid].copy()
subset=set(a.index+1)
issues=issues_all[issues_all.row_number.isin(subset)].copy()
ranked=priority_all[priority_all.asset_id.isin(a.asset_id)].copy()
metrics=summarize_audit(a,issues)
st.sidebar.divider()
st.sidebar.caption(f'{len(a):,} biens sélectionnés | {len(issues):,} anomalies'.replace(',',' '))
st.sidebar.warning('Démonstration fictive : aucune donnée réelle ni affiliation institutionnelle.')
st.markdown('''<div class="hero"><h1>Observatoire du patrimoine immobilier</h1><p>Fiabiliser · Localiser · Prioriser · Décider — données 100 % synthétiques</p></div>''',unsafe_allow_html=True)
st.caption('Prototype de portfolio indépendant — chiffres, adresses et coordonnées générés artificiellement.')
if a.empty:
    st.info('Aucun bien ne correspond aux filtres. Élargis le périmètre dans la barre latérale.');st.stop()

def plot(fig):
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10),height=340,legend_title_text='')
    st.plotly_chart(fig,use_container_width=True)

def download_df(label,df,filename):
    st.download_button(label,df.to_csv(index=False).encode('utf-8-sig'),file_name=filename,mime='text/csv')

if page==SECTIONS[0]:
    k=st.columns(5)
    surf=pd.to_numeric(a.surface_m2,errors='coerce').clip(lower=0).sum()
    for col,label,value in zip(k,['Biens','Surface connue','Fiches conformes','Anomalies','Parcelles référencées'],[f'{len(a):,}'.replace(',',' '),f'{surf/1e6:,.2f} M m²'.replace(',',' '),f"{metrics['conformity_pct']} %",f'{len(issues):,}'.replace(',',' '),str(a.parcel_ref.nunique())]):col.metric(label,value)
    st.info('Les chiffres résument le périmètre filtré. Les anomalies restent consultables dans le Centre de qualité.')
    l,r=st.columns(2)
    with l:plot(px.bar(a.category.value_counts().reset_index(),x='category',y='count',title='Composition du parc par type',labels={'category':'Type','count':'Bâtiments'}))
    with r:plot(px.pie(a.status.value_counts().reset_index(),names='status',values='count',hole=.57,title='Statut du patrimoine'))
    l,r=st.columns(2)
    with l:plot(px.bar(a.district.value_counts().reset_index(),x='district',y='count',title='Répartition par secteur'))
    with r:plot(px.histogram(a,x='energy_rating',category_orders={'energy_rating':list('ABCDEFG')},title='Performance énergétique indicative'))
    st.subheader('Alertes prioritaires')
    st.dataframe(issues[issues.severity.isin(['Critique','Élevée'])][['asset_id','rule','severity','detail']].head(15),hide_index=True,use_container_width=True)

elif page==SECTIONS[1]:
    st.subheader('Recherche et inventaire immobilier')
    st.caption('Sélectionne un bâtiment et explore les anomalies associées.')
    show=['asset_id','name','category','district','status','surface_m2','occupancy_pct','energy_rating','parcel_ref']
    st.dataframe(a[show].head(1000),use_container_width=True,hide_index=True,on_select='ignore')
    st.caption('Aperçu des 1 000 premières lignes du périmètre ; export de la sélection complète ci-dessous.')
    download_df('⬇️ Télécharger le périmètre filtré',a,'patrimoine_selection.csv')
    asset_id=st.selectbox('Consulter rapidement un bien',sorted(a.asset_id.astype(str).unique()),key='lookup')
    record=a[a.asset_id.astype(str)==asset_id].iloc[0]
    st.write(f"**{record['name']}** · {record['category']} · {record['district']} · {record['surface_m2']} m²")
    st.write(f"Référence parcelle : `{record['parcel_ref']}` — statut : {record['status']}")
    related=issues[issues.asset_id.astype(str)==asset_id]
    st.write(f'**{len(related)} anomalie(s) détectée(s)**')
    st.dataframe(related,hide_index=True,use_container_width=True)

elif page==SECTIONS[2]:
    st.subheader('Centre de qualité & registre des anomalies')
    q=st.columns(4)
    for col,label,value in zip(q,['Anomalies','Fiches concernées','Taux de conformité','Règles déclenchées'],[len(issues),metrics['flagged_records'],f"{metrics['conformity_pct']} %",issues.rule.nunique()]):col.metric(label,value)
    left,right=st.columns(2)
    with left:plot(px.bar(issues.rule.value_counts().head(12).reset_index(),x='count',y='rule',orientation='h',title='12 contrôles les plus fréquents'))
    with right:plot(px.pie(issues.severity.value_counts().reset_index(),names='severity',values='count',hole=.5,title='Répartition par gravité'))
    all_rules=sorted(issues.rule.unique())
    f1,f2=st.columns(2)
    chosen_rules=f1.multiselect('Règles de contrôle',all_rules,default=all_rules)
    chosen_sev=f2.multiselect('Niveau de gravité',sorted(issues.severity.unique()),default=sorted(issues.severity.unique()))
    register=issues[issues.rule.isin(chosen_rules)&issues.severity.isin(chosen_sev)].copy()
    st.markdown('**Atelier de qualification (simulation locale)**')
    st.caption('Sélectionne une anomalie et attribue un statut ou un responsable fictif. Ces actions sont stockées uniquement pendant ta session et ne modifient pas les fichiers source.')
    if 'triage' not in st.session_state:st.session_state.triage={}
    if len(register):
        options=register.index.tolist()
        item=st.selectbox('Anomalie à qualifier',options,format_func=lambda idx:f"#{idx} · {register.loc[idx,'asset_id']} — {register.loc[idx,'rule']}")
        c1,c2,c3=st.columns([2,2,1])
        stat=c1.selectbox('Statut',['À vérifier','En cours','Corrigé (simulation)','Validé (simulation)'])
        owner=c2.selectbox('Responsable fictif',['Service foncier','Service patrimoine','Référent données','Service technique'])
        if c3.button('Enregistrer',use_container_width=True):
            st.session_state.triage[str(item)]={'statut_suivi':stat,'responsable':owner}
            st.success('Qualification enregistrée pour cette session de démonstration.')
    register['statut_suivi']=[st.session_state.triage.get(str(i),{}).get('statut_suivi','À vérifier') for i in register.index]
    register['responsable']=[st.session_state.triage.get(str(i),{}).get('responsable','Non affecté') for i in register.index]
    st.dataframe(register.head(1000),use_container_width=True,hide_index=True)
    download_df('⬇️ Exporter le registre filtré',register,'registre_qualite.csv')
    st.warning('Une correction réelle exigerait justification, validation métier, journal persistant et droits d’accès : ce démonstrateur ne remplace pas un outil de production.')

elif page==SECTIONS[3]:
    st.subheader('Cartographie SIG exploratoire')
    coords=a.copy()
    for c in ['latitude','longitude']:coords[c]=pd.to_numeric(coords[c],errors='coerce')
    coords=coords[coords.latitude.between(43.4,43.9)&coords.longitude.between(3.5,4.2)]
    maxpoints=st.slider('Nombre maximum de marqueurs',100,1500,700,100)
    if len(coords)>maxpoints:
        coords=coords.sample(n=maxpoints,random_state=42)
        st.caption(f'Affichage d’un échantillon reproductible de {maxpoints} points pour conserver une carte fluide.')
    st.map(coords,latitude='latitude',longitude='longitude',zoom=10)
    st.caption('Positionnement aléatoire : cette carte ne localise aucun bâtiment ni aucune parcelle réels.')
    st.dataframe(coords[['asset_id','district','category','latitude','longitude']].head(200),hide_index=True,use_container_width=True)

elif page==SECTIONS[4]:
    st.subheader('Simulateur d’aide à la programmation des travaux')
    st.info('Score explicable et budget simulé, sans portée réglementaire ni validation métier : outil de démonstration uniquement.')
    budget=st.slider('Budget fictif disponible (€)',100000,5000000,1500000,50000,format='%d €')
    eligible=ranked[ranked.status!='Cédé'].copy()
    plan,remaining=allocate_budget(eligible,budget)
    m=st.columns(4)
    m[0].metric('Biens priorisés',len(plan));m[1].metric('Budget alloué',f'{(budget-remaining):,.0f} €'.replace(',',' '));m[2].metric('Solde simulé',f'{remaining:,.0f} €'.replace(',',' '));m[3].metric('Score moyen',round(plan.priority_score.mean(),1) if len(plan) else '—')
    l,r=st.columns(2)
    with l:plot(px.histogram(eligible,x='priority_score',nbins=20,title='Distribution des scores de priorité'))
    with r:plot(px.bar(plan.head(15),x='asset_id',y='priority_score',title='Sélection simulée : 15 premiers biens')) if len(plan) else st.info('Aucun projet ne correspond au budget.')
    cols=['asset_id','district','category','priority_score','priority_level','simulated_budget_eur','energy_rating','condition_score']
    st.dataframe(plan[cols].head(250),hide_index=True,use_container_width=True)
    download_df('⬇️ Exporter le scénario retenu',plan[cols],'scenario_travaux.csv')
    with st.expander('Comment est calculé le score ?'):
        st.markdown('**30 % énergie + 30 % résultat des inspections + 20 % taux d’occupation + 20 % coût annuel normalisé.** Les budgets manquants sont estimés par surface. Ces poids sont arbitraires et modifiables dans `src/decision.py`. Le budget est alloué en parcourant les priorités dans l’ordre, sans fractionner les interventions.')

elif page==SECTIONS[5]:
    st.subheader('Fiche patrimoine : vision à 360°')
    key=st.selectbox('Identifiant du bâtiment',sorted(a.asset_id.astype(str).unique()))
    rec=a[a.asset_id.astype(str)==key].iloc[0]
    st.markdown(f"### {rec['name']}")
    p=st.columns(4)
    for col,label,value in zip(p,['Type','Surface','Statut','Énergie'],[rec.category,f'{rec.surface_m2} m²',rec.status,rec.energy_rating]):col.metric(label,str(value))
    l,r=st.columns(2)
    with l:
        st.markdown('**Référentiel et localisation fictive**')
        st.write(f'Secteur : **{rec.district}**')
        st.write(f'Adresse fictive : {rec.address}')
        st.write(f'Parcelle : `{rec.parcel_ref}`')
        st.write(f'Service gestionnaire : {rec.manager_service}')
        related=issues[issues.asset_id.astype(str)==key]
        st.markdown(f'**Qualité : {len(related)} anomalie(s)**')
        st.dataframe(related[['rule','severity','detail']],hide_index=True,use_container_width=True)
    with r:
        st.markdown('**Événements techniques associés**')
        st.write('Inspections répertoriées')
        st.dataframe(inspections[inspections.asset_id.astype(str)==key].head(20),hide_index=True,use_container_width=True)
        st.write('Travaux répertoriés')
        st.dataframe(works[works.asset_id.astype(str)==key].head(20),hide_index=True,use_container_width=True)
    matching=ranked[ranked.asset_id==key]
    if len(matching):st.metric('Score de priorité illustratif',matching.iloc[0].priority_score)

elif page==SECTIONS[6]:
    st.subheader('Catalogue de données et extractions')
    tables={'Bâtiments (filtrés)':a,'Parcelles':parcels,'Inspections':inspections,'Travaux':works,'Anomalies (filtrées)':issues,'Scores de priorité (filtrés)':ranked}
    name=st.selectbox('Choisir un jeu de données',list(tables))
    data=tables[name]
    st.write(f'{len(data):,} lignes × {len(data.columns)} colonnes'.replace(',',' '))
    st.dataframe(data.head(500),hide_index=True,use_container_width=True)
    download_df('⬇️ Exporter le jeu de données',data,'export_'+name.split(' ')[0].lower()+'.csv')
    with st.expander('Dictionnaire des champs'):st.dataframe(pd.DataFrame({'champ':data.columns,'type':[str(t) for t in data.dtypes]}),hide_index=True)

else:
    st.subheader('Bibliothèque SQL PostgreSQL / PostGIS')
    st.info('Exemples de requêtes à lire, copier ou adapter. Aucun SQL arbitraire n’est exécuté et aucune base de données n’est requise pour cette démo.')
    for file in sorted((Path(__file__).resolve().parents[1]/'sql').glob('*.sql')):
        with st.expander(file.name):st.code(file.read_text(encoding='utf-8'),language='sql')

st.divider()
st.caption('© Démonstrateur pédagogique indépendant · Données entièrement fictives · Aucune affiliation avec Montpellier Méditerranée Métropole · Aucun lien avec AS-TECH.')
