from pathlib import Path
class Config:
    # Brightway project name
    PROJECT_NAME = "project_name" # define project name here

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

    # Project directory for exports
    PROJECT_EXPORTS_PATH = (
        ONEDRIVE_PATH
        / "Intranet - Internal Development Projects"
        / "Brightway Open_MA"
        / "data4workshops"
        / "excel_model_example"
        / "exports"
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

    ECOINVENT_BIOSPHERE_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "EcoinventSpold"
        / ECOINVENT_ECOSPOLD_FOLDER_NAME
        / "MasterData"
        / "ElementaryExchanges.xml"
    )

    # BAFU importer settings
    BAFU_ECOSPOLD_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "BAFU"
        / "BAFU-2026 v1_ecoSpold v1"
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
        / "Databases"
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
        / "brightway"
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
    ECOINVENT_BIOSPHERE_EXTRA_NAME = "ecoinvent-3.12-biosphere_extra"
    ECOINVENT_ILUC_NAME = "ecoinvent-3.12-iluc"
    BAFU_DATABASE_NAME = "bafu-2026"
    BAFU_BIOSPHERE_NAME = "biosphere3"

    # 2-0 LCA brand identity

    COLORS = {
        # Core brand colours
        "passion_red": "#F04D46",
        "future_green": "#BFD2D0",
        "reliable_blue": "#0075C5",
        "dark_grey": "#353B37",
        "data_blue": "#CCD2EA",
        "nature_green": "#73876B",
        "white": "#FFFFFF",
        # Supplemental categorical colours for charts with several series
        "orange": "#E69F00",
        "purple": "#8E63A9",
        "teal": "#2A9D8F",
        "yellow": "#C9A227",
        "brown": "#9C6644",
        "magenta": "#CC79A7",
        "sky_blue": "#56B4E9",
        "slate": "#5B6770",
        "olive": "#6B7D2A",
        # Approved gradients from the 2-0 LCA design system
        "red_2": "#E9605A",
        "red_3": "#E2736D",
        "red_4": "#DB8681",
        "red_5": "#D49995",
        "red_6": "#CDACA9",
        "red_7": "#C6BFBC",
        "blue_2": "#A4C5CE",
        "blue_3": "#88B7CD",
        "blue_4": "#6DAACB",
        "blue_5": "#529DCA",
        "blue_6": "#3790C8",
        "blue_7": "#1B82C7",
    }

    PALETTE = (
        COLORS["passion_red"],
        COLORS["reliable_blue"],
        COLORS["nature_green"],
        COLORS["orange"],
        COLORS["purple"],
        COLORS["teal"],
        COLORS["yellow"],
        COLORS["brown"],
        COLORS["magenta"],
        COLORS["sky_blue"],
        COLORS["slate"],
        COLORS["olive"],
    )

    RED_GRADIENT = (
        COLORS["passion_red"],
        COLORS["red_2"],
        COLORS["red_3"],
        COLORS["red_4"],
        COLORS["red_5"],
        COLORS["red_6"],
        COLORS["red_7"],
    )

    BLUE_GRADIENT = (
        COLORS["data_blue"],
        COLORS["blue_2"],
        COLORS["blue_3"],
        COLORS["blue_4"],
        COLORS["blue_5"],
        COLORS["blue_6"],
        COLORS["blue_7"],
        COLORS["reliable_blue"],
    )

    TITLE_FONT = "Roc Grotesk"
    BODY_FONT = "TT Commons Pro"
