from pathlib import Path
from tempfile import TemporaryDirectory

import bw2data as bd
import bw2io as bi
import pandas as pd


def prepare_extra_biosphere_import(source_path: Path, project_name: str):
    """Prepare an extra biosphere importer without writing the database."""

    bd.projects.set_current(project_name)

    importer = bi.ExcelImporter(source_path)
    importer.apply_strategies()

    return importer


def prepare_iluc_import(
    source_path: Path,
    project_name: str,
    ecoinvent_database_name: str,
    biosphere_database_name: str,
    extra_biosphere_database_name: str,
    sheet_name: str = "BW inventory",
):
    """Prepare and link the iLUC importer without writing the database."""

    bd.projects.set_current(project_name)

    required_databases = {
        ecoinvent_database_name,
        biosphere_database_name,
        extra_biosphere_database_name,
    }

    missing_databases = required_databases - set(bd.databases)

    if missing_databases:
        raise RuntimeError(
            "Import the required background databases first: "
            + ", ".join(sorted(missing_databases))
        )

    with TemporaryDirectory(prefix="iluc_import_") as temp_directory:
        temporary_path = Path(temp_directory) / "iluc_import.xlsx"

        inventory = pd.read_excel(source_path, sheet_name=sheet_name)
        inventory.to_excel(
            temporary_path,
            sheet_name=sheet_name,
            index=False,
            engine="openpyxl",
        )

        importer = bi.ExcelImporter(temporary_path)
        importer.apply_strategies()

        # Link exchanges within the imported database.
        importer.match_database(
            fields=["name", "location", "unit", "reference product"]
        )
        importer.match_database(
            fields=["name", "location", "unit"]
        )

        # Link consequential ecoinvent exchanges.
        importer.match_database(
            db_name=ecoinvent_database_name,
            fields=["name", "location", "unit", "reference product"],
        )
        importer.match_database(
            db_name=ecoinvent_database_name,
            fields=["name", "location", "unit"],
        )

        # Link elementary flows.
        importer.match_database(
            db_name=biosphere_database_name,
            fields=["name", "categories", "unit"],
        )

        # Link extra elementary flows.
        importer.match_database(
            db_name=extra_biosphere_database_name,
            fields=["name", "categories", "unit"],
        )

        importer.statistics()

        return importer