import json
from superset.app import create_app

def setup():
    app = create_app()
    app.app_context().push()

    from superset.extensions import db
    from superset.models.core import Database
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard

    # 1. Create Database
    db_name = 'Materials'
    database = db.session.query(Database).filter_by(database_name=db_name).first()
    if not database:
        print(f"Creating database {db_name}...")
        database = Database(
            database_name=db_name,
            sqlalchemy_uri='sqlite:////app/data/materials.db'
        )
        db.session.add(database)
        db.session.commit()

    # 2. Create Datasets
    tables = ['properties_core', 'materials', 'formulas']
    table_objs = {}
    for table_name in tables:
        table = db.session.query(SqlaTable).filter_by(table_name=table_name, database_id=database.id).first()
        if not table:
            print(f"Registering dataset {table_name}...")
            table = SqlaTable(table_name=table_name, database=database)
            db.session.add(table)
            db.session.commit()
            table.fetch_metadata()
        table_objs[table_name] = table

    # 3. Create Charts (Slices)
    prop_core = table_objs['properties_core']
    
    charts_data = [
        {
            "slice_name": "Materials by Crystal System",
            "viz_type": "dist_bar",
            "params": {
                "metrics": ["count"],
                "groupby": ["crystal_system"],
                "row_limit": 10000,
                "x_axis_label": "Crystal System",
                "y_axis_label": "Count"
            }
        },
        {
            "slice_name": "Metallic vs Non-Metallic",
            "viz_type": "pie",
            "params": {
                "metric": "count",
                "groupby": ["is_metal"],
                "row_limit": 10000
            }
        },
        {
            "slice_name": "Density Distribution",
            "viz_type": "histogram",
            "params": {
                "all_columns_x": "density",
                "row_limit": 50000,
                "color_scheme": "supersetColors"
            }
        },
        {
            "slice_name": "Band Gap Distribution",
            "viz_type": "histogram",
            "params": {
                "all_columns_x": "band_gap",
                "row_limit": 50000,
                "color_scheme": "supersetColors"
            }
        },
        {
            "slice_name": "Stability Landscape",
            "viz_type": "scatter",
            "params": {
                "x": "formation_energy_per_atom",
                "y": "energy_above_hull",
                "groupby": ["crystal_system"],
                "entity": "material_id",
                "row_limit": 10000
            }
        }
    ]

    slices = []
    for chart_data in charts_data:
        slc = db.session.query(Slice).filter_by(slice_name=chart_data["slice_name"]).first()
        if not slc:
            print(f"Creating chart {chart_data['slice_name']}...")
            slc = Slice(
                slice_name=chart_data["slice_name"],
                datasource_type='table',
                datasource_id=prop_core.id,
                viz_type=chart_data["viz_type"],
                params=json.dumps(chart_data["params"])
            )
            db.session.add(slc)
            db.session.commit()
        slices.append(slc)

    # 4. Create Dashboard
    dash_title = "1 - Material Landscape Overview"
    dashboard = db.session.query(Dashboard).filter_by(dashboard_title=dash_title).first()
    if not dashboard:
        print(f"Creating dashboard {dash_title}...")
        dashboard = Dashboard(
            dashboard_title=dash_title,
            slug="material-landscape",
            slices=slices,
            published=True
        )
        db.session.add(dashboard)
        db.session.commit()
    else:
        # Update slices if dashboard exists
        dashboard.slices = slices
        db.session.commit()

    print("Dashboard setup complete!")

if __name__ == "__main__":
    setup()
