import os
from typing import Optional, List

import pandas as pd
from mp_api.client import MPRester
from pydantic import BaseModel
from matminer.datasets import load_dataset  # type: ignore


class MaterialData(BaseModel):
    material_id: str
    formula: str
    elements: str
    density: float
    band_gap: float
    is_metal: bool
    formation_energy_per_atom: Optional[float] = None
    energy_above_hull: Optional[float] = None
    volume: Optional[float] = None
    theoretical: bool
    crystal_system: Optional[str] = None


class DataImporter:
    def __init__(self) -> None:
        self.api_key = os.environ.get("MP_API_KEY")
        if not self.api_key:
            raise ValueError("MP_API_KEY environment variable not set")

    def _clean_dataframe_for_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        import json

        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: (
                        json.dumps(x.as_dict())
                        if hasattr(x, "as_dict")
                        else (str(x).replace("\n", "\\n") if isinstance(x, str) else x)
                    )
                )
        return df

    def import_battery_dataset(self, output_file: str, force: bool = False) -> None:
        """
        Import battery dataset from Matminer datasets and save to CSV.  use matbench
            https://matbench.readthedocs.io/en/latest/datasets/

        Args:
            output_file: Path to save the output CSV file.
            force: If True, overwrite the file if it exists.
        """
        if not force and os.path.exists(output_file):
            print(
                f"Dataset already exists at {output_file}. Skipping. Use --force to rewrite."
            )
            return

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        df = load_dataset("matbench_expt_gap")
        df = self._clean_dataframe_for_csv(df)
        df.to_csv(output_file, index=False)
        print(df.head())

    def import_alternative_datasets(self, output_dir: str, force: bool = False) -> None:
        """
        Import multiple alternative datasets requested by the user.
        Downloads: dielectric_constant, elastic_tensor_2015, matbench_phonons, matbench_mp_gap, steel_strength.
        """
        datasets_to_download = [
            "dielectric_constant",
            "elastic_tensor_2015",
            "matbench_phonons",
            "matbench_mp_gap",
            "steel_strength",
        ]

        os.makedirs(output_dir, exist_ok=True)

        for ds_name in datasets_to_download:
            output_file = os.path.join(output_dir, f"{ds_name}.csv")
            if not force and os.path.exists(output_file):
                print(
                    f"Dataset already exists at {output_file}. Skipping. Use --force to rewrite."
                )
                continue

            print(f"Fetching dataset {ds_name}...")
            df = load_dataset(ds_name)
            df = self._clean_dataframe_for_csv(df)
            df.to_csv(output_file, index=False)
            print(f"Saved {ds_name} to {output_file}")

    def import_materials(self, output_file: str, force: bool = False) -> None:
        if not force and os.path.exists(output_file):
            print(
                f"Dataset already exists at {output_file}. Skipping. Use --force to rewrite."
            )
            return

        fields = [
            "material_id",
            "formula_pretty",
            "elements",
            "density",
            "band_gap",
            "is_metal",
            "formation_energy_per_atom",
            "energy_above_hull",
            "volume",
            "theoretical",
            "symmetry",
        ]

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        chunk_size = 1000
        is_first_chunk = True
        page = 1

        with MPRester(self.api_key, use_document_model=False) as mpr:
            # We paginate manually using _page to prevent mp-api from trying to
            # download and buffer the entire 160k dataset into memory at once.
            while True:
                docs = mpr.materials.summary.search(
                    fields=fields, num_chunks=1, chunk_size=chunk_size, _page=page
                )

                if not docs:
                    # No more records found
                    break

                materials_data: List[dict] = []
                for doc in docs:
                    crystal_sys = None
                    symmetry = doc.get("symmetry")
                    if isinstance(symmetry, dict):
                        c_sys = symmetry.get("crystal_system")
                        crystal_sys = str(c_sys) if c_sys else None

                    # Validate and format with Pydantic
                    validated_material = MaterialData(
                        material_id=str(doc.get("material_id")),
                        formula=str(doc.get("formula_pretty")),
                        elements=",".join([str(e) for e in doc.get("elements", [])]),
                        density=float(doc.get("density", 0.0) or 0.0),
                        band_gap=float(doc.get("band_gap", 0.0) or 0.0),
                        is_metal=bool(doc.get("is_metal")),
                        formation_energy_per_atom=float(
                            doc.get("formation_energy_per_atom")
                        )
                        if doc.get("formation_energy_per_atom") is not None
                        else None,
                        energy_above_hull=float(doc.get("energy_above_hull"))
                        if doc.get("energy_above_hull") is not None
                        else None,
                        volume=float(doc.get("volume"))
                        if doc.get("volume") is not None
                        else None,
                        theoretical=bool(doc.get("theoretical")),
                        crystal_system=str(crystal_sys) if crystal_sys else None,
                    )
                    materials_data.append(validated_material.model_dump())

                # Write chunk to disk
                if materials_data:
                    df = pd.DataFrame(materials_data)
                    df.to_csv(
                        output_file,
                        mode="a" if not is_first_chunk else "w",
                        header=is_first_chunk,
                        index=False,
                    )
                    is_first_chunk = False
                    print(
                        f"Flushed page {page} ({len(materials_data)} records) to disk..."
                    )

                # Move to next page
                page += 1
        print(df.head())

    def export_to_sql(self, data_dir: str, db_name: str = "materials.db") -> None:
        """
        Export all CSV files in the data directory to a local SQLite database
        using the relational DataTransformer pipeline.
        """
        from src.data_importer.data_transformer import DataTransformer

        transformer = DataTransformer(data_dir=data_dir)
        transformer.process_and_export(db_name=db_name)
