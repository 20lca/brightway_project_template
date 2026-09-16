from pathlib import Path
class Config:

    # Brightway database names
    ECOINVENT_ALCA_NAME = "ecoinvent-3.12-cutoff"
    ECOINVENT_CLCA_NAME = "ecoinvent-3.12-consequential"
    BIOSPHERE_NAME = "ecoinvent-3.12-biosphere"
    BIOSPHERE_EXTRA_NAME = "ecoinvent-3.12-biosphere-extra"
    ECOINVENT_ILUC_NAME = "ecoinvent-3.12-iluc"

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


    # Brightway project name
    PROJECT_NAME = "brightway_project" # define project name here

    # Company OneDrive
    ONEDRIVE_PATH = Path.home() / "OneDrive - 2.-0 LCA Consultants ApS"

    # Project folder
    PROJECT_FOLDER = "PROJECTNAME_PROJECTNUMBER"

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

