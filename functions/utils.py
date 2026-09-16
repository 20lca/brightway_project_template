from pathlib import Path
class Config:
    # Define Brighway database names
    ECOINVENT_ALCA_NAME = "ecoinvent-3.12-cutoff"
    ECOINVENT_CLCA_NAME = "ecoinvent-3.12-consequential"
    BIOSPHERE_NAME = "ecoinvent-3.12-biosphere"
    BIOSPHERE_EXTRA_NAME = "biosphere3-extra"
    ECOINVENT_ILUC_NAME = "ecoinvent-3.12-iluc"

    # Define Brightway project name
    PROJECT_NAME = "brightway_project"

    # Define project paths
    ONEDRIVE_PATH = Path.home() / "OneDrive - 2.-0 LCA Consultants ApS"
    PROJECT_FOLDER = "PROJECTNAME_PROJECTNUMBER"

    # First, look for the project directly in the OneDrive folder
    PROJECT_DIRECTORY_PATH = ONEDRIVE_PATH / PROJECT_FOLDER / "Model"

    # If it is not there, look in Active Projects instead
    if not PROJECT_DIRECTORY_PATH.is_dir():
        PROJECT_DIRECTORY_PATH = (
            ONEDRIVE_PATH
            / "Active Projects"
            / PROJECT_FOLDER
            / "Model"
        )