import os
import argparse
from src.data_importer.data_importer import DataImporter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force", action="store_true", help="Force overwrite existing files"
    )
    parser.add_argument(
        "--target",
        choices=["all", "core", "battery", "alternative"],
        default="all",
        help="Target specific dataset to import (default: all)",
    )
    parser.add_argument(
        "--action",
        choices=["download", "import"],
        default="download",
        help="Action to perform: download CSVs or import to MySQL/SQLite",
    )
    args = parser.parse_args()

    di = DataImporter()

    if args.action == "download":
        if args.target in ["all", "core"]:
            output_path = os.path.join("data", "core_materials.csv")
            print(f"Importing materials to {output_path}...")
            di.import_materials(output_path, force=args.force)

        if args.target in ["all", "battery"]:
            battery_path = os.path.join("data", "battery_materials.csv")
            print(f"Importing battery dataset to {battery_path}...")
            di.import_battery_dataset(battery_path, force=args.force)

        if args.target in ["all", "alternative"]:
            print("Importing alternative datasets to data/...")
            di.import_alternative_datasets("data", force=args.force)

        print("Download complete.")

    elif args.action == "import":
        print("Exporting downloaded CSVs to SQLite database...")
        di.export_to_sql("data")
        print("Import complete.")


if __name__ == "__main__":
    main()
