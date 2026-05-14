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

    db_name = 'Materials'
    database = db.session.query(Database).filter_by(database_name=db_name).first()

    if not database:
        print("Database not found. Exiting.")
        return

    # Fetch all datasets into a dict
    datasets = {t.table_name: t for t in db.session.query(SqlaTable).filter_by(database_id=database.id).all()}

    # Fetch all dashboards into a dict
    dashboards = {d.dashboard_title: d for d in db.session.query(Dashboard).all()}

    charts_config = [
        # DASHBOARD 2
        {
            "dashboard": "2 - Battery Material Intelligence",
            "slice_name": "Battery Material Explorer",
            "dataset": "properties_core",
            "viz_type": "table",
            "params": {"all_columns": ["material_id", "density", "band_gap", "formation_energy_per_atom", "energy_above_hull"], "row_limit": 1000}
        },
        {
            "dashboard": "2 - Battery Material Intelligence",
            "slice_name": "Conductivity vs Density",
            "dataset": "properties_core",
            "viz_type": "scatter",
            "params": {"x": "density", "y": "band_gap", "groupby": ["is_metal"], "row_limit": 5000}
        },
        {
            "dashboard": "2 - Battery Material Intelligence",
            "slice_name": "Experimental vs Calculated Band Gaps",
            "dataset": "Virtual: Battery Band Gaps (Expt vs Calc)",
            "viz_type": "scatter",
            "params": {"x": "gap pbe", "y": "gap expt", "row_limit": 5000}
        },
        {
            "dashboard": "2 - Battery Material Intelligence",
            "slice_name": "Top Candidate Materials Ranking",
            "dataset": "properties_core",
            "viz_type": "table",
            "params": {"all_columns": ["material_id", "density", "band_gap", "energy_above_hull"], "row_limit": 100}
        },

        # DASHBOARD 3
        {
            "dashboard": "3 - Stability & Conductivity Analytics",
            "slice_name": "Band Gap vs Dielectric Constant",
            "dataset": "Virtual: Conductivity & Dielectric Correlation",
            "viz_type": "scatter",
            "params": {"x": "band_gap", "y": "e_total", "row_limit": 5000}
        },
        {
            "dashboard": "3 - Stability & Conductivity Analytics",
            "slice_name": "Stability vs Elasticity",
            "dataset": "Virtual: Stability vs Elasticity",
            "viz_type": "scatter",
            "params": {"x": "energy_above_hull", "y": "K_VRH", "row_limit": 5000}
        },
        {
            "dashboard": "3 - Stability & Conductivity Analytics",
            "slice_name": "Ferroelectric Candidate Discovery",
            "dataset": "properties_dielectric",
            "viz_type": "table",
            "params": {"all_columns": ["material_id", "pot_ferroelectric", "e_total", "n"], "row_limit": 1000}
        },
        {
            "dashboard": "3 - Stability & Conductivity Analytics",
            "slice_name": "Refractive Index Analysis",
            "dataset": "properties_dielectric",
            "viz_type": "histogram",
            "params": {"all_columns_x": "n", "row_limit": 5000}
        },

        # DASHBOARD 4
        {
            "dashboard": "4 - Mechanical & Structural Intelligence",
            "slice_name": "Elastic Anisotropy Distribution",
            "dataset": "properties_elastic",
            "viz_type": "histogram",
            "params": {"all_columns_x": "elastic_anisotropy", "row_limit": 5000}
        },
        {
            "dashboard": "4 - Mechanical & Structural Intelligence",
            "slice_name": "Bulk vs Shear Modulus",
            "dataset": "properties_elastic",
            "viz_type": "scatter",
            "params": {"x": "K_VRH", "y": "G_VRH", "row_limit": 5000}
        },
        {
            "dashboard": "4 - Mechanical & Structural Intelligence",
            "slice_name": "Poisson Ratio Distribution",
            "dataset": "properties_elastic",
            "viz_type": "histogram",
            "params": {"all_columns_x": "poisson_ratio", "row_limit": 5000}
        },
        {
            "dashboard": "4 - Mechanical & Structural Intelligence",
            "slice_name": "Steel Alloy Strength Analysis",
            "dataset": "experiments_steel",
            "viz_type": "scatter",
            "params": {"x": "tensile strength", "y": "elongation", "row_limit": 5000}
        },

        # DASHBOARD 5
        {
            "dashboard": "5 - AI Recommendation Workbench",
            "slice_name": "Material Recommendation Table",
            "dataset": "properties_core",
            "viz_type": "table",
            "params": {"all_columns": ["material_id", "density", "band_gap", "formation_energy_per_atom", "is_metal"], "row_limit": 100}
        },
        {
            "dashboard": "5 - AI Recommendation Workbench",
            "slice_name": "Multi-Objective Optimization Plot",
            "dataset": "properties_core",
            "viz_type": "scatter",
            "params": {"x": "density", "y": "band_gap", "row_limit": 5000}
        },

        # DASHBOARD 6
        {
            "dashboard": "6 - Data Quality & Coverage",
            "slice_name": "Missing Values Analysis",
            "dataset": "properties_core",
            "viz_type": "table",
            "params": {"metrics": ["count"], "row_limit": 100}
        },
        {
            "dashboard": "6 - Data Quality & Coverage",
            "slice_name": "Total Materials Processed",
            "dataset": "materials",
            "viz_type": "big_number_total",
            "params": {"metric": "count"}
        }
    ]

    for config in charts_config:
        ds = datasets.get(config["dataset"])
        if not ds:
            print(f"Dataset {config['dataset']} not found! Skipping {config['slice_name']}.")
            continue

        slc = db.session.query(Slice).filter_by(slice_name=config["slice_name"]).first()
        if not slc:
            print(f"Creating chart: {config['slice_name']}...")
            slc = Slice(
                slice_name=config["slice_name"],
                datasource_type='table',
                datasource_id=ds.id,
                viz_type=config["viz_type"],
                params=json.dumps(config["params"])
            )
            db.session.add(slc)
            db.session.commit()
        
        dash = dashboards.get(config["dashboard"])
        if dash:
            if slc not in dash.slices:
                print(f"Attaching {config['slice_name']} to {config['dashboard']}...")
                dash.slices.append(slc)
                db.session.commit()

    print("All charts for Dashboards 2-6 have been generated and attached!")

if __name__ == "__main__":
    setup()
