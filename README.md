# 🏛️ Métropole Patrimoine Data 360 — version enrichie

**Démonstrateur personnel et indépendant de pilotage et de fiabilisation du patrimoine foncier et immobilier.** Données **intégralement synthétiques**, aucune affiliation à Montpellier Méditerranée Métropole, aucun accès à ses systèmes, à AS-TECH ou au cadastre officiel.

## Jeu de données

| Fichier | Enregistrements | Usage |
|---|---:|---|
| `data/assets_synthetic.csv` | 6 500 | Bâtiments fictifs, occupation, coûts, surfaces, géolocalisation |
| `data/parcels_synthetic.csv` | 3 200 | Parcelles fictives, zonage, valeur, propriétaires génériques |
| `data/inspections_synthetic.csv` | 12 500 | Inspections simulées et constats |
| `data/works_synthetic.csv` | 1 800 | Travaux fictifs, budgets et avancement |

**24 000 lignes**, générées de manière déterministe. Des erreurs sont injectées exprès afin de montrer la fiabilisation : doublons d'identifiants, valeurs hors bornes, champs manquants, incohérences occupation/vacance, références orphelines, coordonnées aberrantes, statuts hors référentiel, etc. Les localisations sont simulées et **ne décrivent aucun bâtiment réel**.

## Modules Streamlit

1. **Tableau de bord** — KPIs et typologies de patrimoine.
2. **Fiabilisation** — audit automatique multi-règles, niveaux de gravité, registre d'anomalies exportable.
3. **Cartographie SIG** — points fictifs interactifs.
4. **Patrimoine et parcelles** — jointures de référentiels, surfaces, classes énergétiques.
5. **Inspections et travaux** — conformité, budgets et avancement.
6. **Référentiel et exports** — consultation et CSV téléchargeable.
7. **Explorateur SQL** — schémas, contrôles et reporting PostgreSQL/PostGIS.

**Limites** : application en lecture seule, aucune persistance des statuts d'anomalies, aucune authentification, aucune connexion automatique entre Streamlit et PostgreSQL. La base SQL est **optionnelle** et présentée comme exercice d'ingénierie de données. Les coûts et valeurs foncières fictifs ne doivent pas servir à des décisions réelles.

## Démarrer sous Windows — sans Docker

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/dashboard.py
```

Pour tester : `python -m pytest -q`.

## Publier sur GitHub et déployer

Créer un dépôt public `metropole-patrimoine-data-360` et y déposer le contenu de ce dossier (ne pas joindre une deuxième archive dans le dépôt). Streamlit Community Cloud : choisir **`app/dashboard.py`** comme point d'entrée. Aucun secret requis.

Pour PostgreSQL optionnel, voir [`sql/README.md`](sql/README.md) et `docker-compose.yml`.

## Architecture

```text
app/dashboard.py            interface Streamlit
src/advanced_quality.py     contrôles métiers additionnels
src/quality.py              contrôles de base
src/data_access.py          chargement CSV
sql/                       schéma, vérifications, requêtes de pilotage
data/                      4 fichiers de données fictives
tests/                     tests pytest
.github/workflows/          tests continus
```

## Sources et transparence

Démonstrateur autonome conçu pour illustrer des missions de gestion du patrimoine public. L'approche d'architecture de données géospatiales a été **inspirée** par le dépôt public [danmaps/geospatial-data-engineering-demo](https://github.com/danmaps/geospatial-data-engineering-demo), mais le présent code est une nouvelle implémentation, **pas une copie** de ses fichiers. Pour reprendre du code tiers, vérifier sa licence et respecter ses conditions. Le projet ne représente ni une commande ni un livrable de la collectivité.

## Optimisations de fluidité
- L'audit qualité des 6 500 fiches est mémorisé via `st.cache_data` : modifier un filtre ne recalcule plus toutes les règles.
- La carte affiche un échantillon reproductible d'au plus 1 200 points, sans altérer les indicateurs calculés sur le jeu complet.
- L'aperçu des anomalies est limité à 1 000 lignes et celui des référentiels à 500 ; les exports conservent les données complètes.
- À chaque modification GitHub, Streamlit Community Cloud redéploie l'application ; un premier chargement après veille peut rester plus long.


## Version premium — fonctions ajoutées

- Vue exécutive avec filtres globaux par secteur, type de bâtiment, et recherche directe par identifiant.
- Recherche patrimoniale et fiche 360° du bâtiment (anomalies, inspections, travaux).
- Centre de qualité avec qualification des anomalies (statuts stockés **en session uniquement**, aucune persistance).
- Simulateur de priorisation des travaux, score transparent et budget fictif interactif.
- Carte plafonnée à 700 marqueurs par défaut pour une navigation plus fluide.
- Catalogue exportable des données et exemples SQL.

### Méthodologie et réserves
Les données sont entièrement synthétiques. Le scoring est heuristique, ses coefficients sont arbitraires : il ne constitue ni une décision de travaux, ni une estimation immobilière réelle. Les montants simulés ne sont pas des devis. La qualification des anomalies dans l'interface n'est pas persistée, et le logiciel AS-TECH n'est pas intégré. La démonstration n'est pas affiliée à la Métropole de Montpellier.

### Déploiement Streamlit
Fichier principal : `app/dashboard.py` ; dépendances : `requirements.txt`. L'application lit des CSV inclus dans `data/` et ne nécessite aucun serveur PostgreSQL pour l'affichage.
