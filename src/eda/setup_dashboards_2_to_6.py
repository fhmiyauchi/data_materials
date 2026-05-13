import json
from superset.app import create_app

def setup():
    app = create_app()
    app.app_context().push()

    from superset.extensions import db
    from superset.models.core import Database
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.dashboard import Dashboard

    database = db.session.query(Database).filter_by(database_name='NEDGEX_Materials').first()

    # 1. Register Remaining Physical Tables
    tables = [
        'experiments_battery', 
        'structures_mp_gap', 
        'properties_dielectric', 
        'properties_elastic', 
        'experiments_steel'
    ]
    for table_name in tables:
        table = db.session.query(SqlaTable).filter_by(table_name=table_name, database_id=database.id).first()
        if not table:
            print(f"Registering physical dataset {table_name}...")
            table = SqlaTable(table_name=table_name, database=database)
            db.session.add(table)
            db.session.commit()
            try:
                table.fetch_metadata()
            except Exception as e:
                print(f"Warning fetching metadata for {table_name}: {e}")

    # 2. Register Virtual Datasets (SQL Queries)
    virtual_datasets = [
        {
            "name": "Virtual: Battery Band Gaps (Expt vs Calc)",
            "sql": 'SELECT b.standard_formula, b."gap expt", p."gap pbe" FROM experiments_battery b JOIN structures_mp_gap p ON b.standard_formula = p.standard_formula'
        },
        {
            "name": "Virtual: Conductivity & Dielectric Correlation",
            "sql": "SELECT c.material_id, c.band_gap, d.e_total FROM properties_core c JOIN properties_dielectric d ON c.material_id = d.material_id"
        },
        {
            "name": "Virtual: Stability vs Elasticity",
            "sql": "SELECT c.material_id, c.energy_above_hull, e.K_VRH FROM properties_core c JOIN properties_elastic e ON c.material_id = e.material_id"
        }
    ]

    for vd in virtual_datasets:
        table = db.session.query(SqlaTable).filter_by(table_name=vd["name"], database_id=database.id).first()
        if not table:
            print(f"Registering virtual dataset {vd['name']}...")
            table = SqlaTable(
                table_name=vd["name"],
                database=database,
                sql=vd["sql"],
                is_sqllab_view=True
            )
            db.session.add(table)
            db.session.commit()
            try:
                table.fetch_metadata()
            except Exception as e:
                print(f"Warning fetching metadata for {vd['name']}: {e}")

    # 3. Create Dashboard Shells
    dashboards = [
        ("2 - Battery Material Intelligence", "battery-material-intelligence"),
        ("3 - Stability & Conductivity Analytics", "stability-conductivity-analytics"),
        ("4 - Mechanical & Structural Intelligence", "mechanical-structural-intelligence"),
        ("5 - AI Recommendation Workbench", "ai-recommendation-workbench"),
        ("6 - Data Quality & Coverage", "data-quality-coverage")
    ]

    for title, slug in dashboards:
        dashboard = db.session.query(Dashboard).filter_by(dashboard_title=title).first()
        if not dashboard:
            print(f"Creating dashboard shell {title}...")
            dashboard = Dashboard(
                dashboard_title=title,
                slug=slug,
                published=True
            )
            db.session.add(dashboard)
            db.session.commit()

    print("Dashboards 2-6 Setup Complete!")

if __name__ == "__main__":
    setup()
