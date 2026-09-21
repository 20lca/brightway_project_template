from pathlib import Path
class Config:

    # Brightway project name
    PROJECT_NAME = "test_project" # define project name here

    # Company OneDrive
    ONEDRIVE_PATH = Path.home() / "OneDrive - 2.-0 LCA Consultants ApS"

    # Project directory
    PROJECT_DIRECTORY_PATH = (
        ONEDRIVE_PATH
        / "Intranet - Internal Development Projects"
        / "Brightway Open_MA"
        / "data4workshops"
        / "excel_model_example"
    )

    # Ecoinvent settings for web install
    ECOINVENT_USERNAME = "tw20lca" # input your username here
    ECOINVENT_PASSWORD = "20LCAcph" # input your password here
    ECOINVENT_VERSION = "3.12" # input your ecoinvent version here
    ECOINVENT_SYSTEM_MODEL = "consequential"  # input your system model here (can be cutoff / apos / consequential / EN15804)

    # Ecoinvent settings for manual install
    ECOINVENT_ECOSPOLD_FOLDER_NAME = "ecoinvent 3.12_consequential_ecoSpold02" # define the ecoinvent ecoSpold folder name here

    ECOINVENT_ECOSPOLD_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "EcoinventSpold"
        / ECOINVENT_ECOSPOLD_FOLDER_NAME
        / "datasets"
    )

    # BAFU importer settings
    BAFU_ECOSPOLD_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "BAFU"
        / "BAFU-2026 ecospold1"
        / "ecoSpold files"
    )

    BAFU_MAPPING_FILE_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "BAFU"
        / "elementary_flows_mapping.csv"
    )

    # EXIOBASE importer settings
    EXIOBASE_DATABASE_NAME = "exiobase3316b2"
    EXIOBASE_BIOSPHERE_NAME = "biosphere3"
    EXIOBASE_EXTRA_BIOSPHERE_NAME = "exiobase3316_extra_biosphere_b2"

    EXIOBASE_CSV_PATH = (
        ONEDRIVE_PATH
        / "EXIOBASE_BW"
        / "exiobase_v3.3.16b2.CSV"
    )

    # BONSAI importer settings
    BONSAI_DATABASE_VERSION = "v2.4.1"
    BONSAI_DATABASE_NAME = f"BONSAI {BONSAI_DATABASE_VERSION}"
    BONSAI_BIOSPHERE_NAME = "biosphere3"
    BONSAI_BIOSPHERE_DATABASE_NAME = f"{BONSAI_DATABASE_NAME} biosphere"

    BONSAI_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "BONSAI"
        / BONSAI_DATABASE_VERSION
    )

    # iLUC and extra biosphere importer settings
    EXTRA_BIOSPHERE_FILE_NAME = "extra_biosphere.xlsx"
    ILUC_FILE_NAME = "iLUC_for_bw_ei312_conseq.xlsx"
    ILUC_SHEET_NAME = "BW inventory"

    EXTRA_BIOSPHERE_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "iLUC_BW"
        / EXTRA_BIOSPHERE_FILE_NAME
    )

    ILUC_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "iLUC_BW"
        / ILUC_FILE_NAME
    )

    # Brightway database names
    ECOINVENT_ALCA_NAME = "ecoinvent-3.12-cutoff"
    ECOINVENT_CLCA_NAME = "ecoinvent-3.12-consequential"
    ECOINVENT_BIOSPHERE_NAME = "ecoinvent-3.12-biosphere"
    ECOINVENT_BIOSPHERE_ALT_NAME = "biosphere3"
    ECOINVENT_BIOSPHERE_EXTRA_NAME = "ecoinvent-3.12-biosphere-extra"
    ECOINVENT_ILUC_NAME = "ecoinvent-3.12-iluc"
    BAFU_DATABASE_NAME = "bafu"
    BAFU_BIOSPHERE_NAME = "biosphere3"