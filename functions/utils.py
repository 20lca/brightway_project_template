from pathlib import Path
class Config:

    # Brightway project name
    PROJECT_NAME = "brightway_project" # define project name here
    
    # Project folder
    PROJECT_FOLDER = "PROJECTNAME_PROJECTNUMBER"

    # Company OneDrive
    ONEDRIVE_PATH = Path.home() / "OneDrive - 2.-0 LCA Consultants ApS"

    # Project directory
    PROJECT_DIRECTORY_PATH = (
        ONEDRIVE_PATH
        / PROJECT_FOLDER
        / "Model"
    )

    if not PROJECT_DIRECTORY_PATH.is_dir():
        PROJECT_DIRECTORY_PATH = (
            ONEDRIVE_PATH
            / "Active Projects"
            / PROJECT_FOLDER
            / "Model"
        )    

    # Brightway database names
    ECOINVENT_ALCA_NAME = "ecoinvent-3.12-cutoff"
    ECOINVENT_CLCA_NAME = "ecoinvent-3.12-consequential"
    ECOINVENT_BIOSPHERE_NAME = "ecoinvent-3.12-biosphere"
    ECOINVENT_BIOSPHERE_ALT_NAME = "biosphere3"
    ECOINVENT_BIOSPHERE_EXTRA_NAME = "ecoinvent-3.12-biosphere-extra"
    ECOINVENT_ILUC_NAME = "ecoinvent-3.12-iluc"
    BAFU_DATABASE_NAME = "bafu"
    BAFI_BIOSPHERE_NAME = "biosphere3"

    # Ecoinvent settings for web install
    ECOINVENT_USERNAME = "usernamehere" # input your username here
    ECOINVENT_PASSWORD = "passwordhere" # input your password here
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
        / "BAFU-2025 ecospold1"
        / "BAFU-2025_LCI ecoSpold v1 (for other softwares)"
        / "LCI ecoSpold v1 Files"
    )

    BAFU_MAPPING_FILE_PATH = (
        ONEDRIVE_PATH
        / "Databases"
        / "BAFU"
        / "elementary_flows_mapping.csv"
    )