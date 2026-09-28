# brightway_project_template
This is the first draft of a template repository for starting new brightway project. 

The goal of the repository is for the user to be able to use it as a starting point or template for creating new brightway projects.

The user can create a new repository from this template and customise it to their needs.

With this repository the user is able to import the background database(s) they need from this list:
- BONSAI
- ecoinvent
- EXIOBASE
- BAFU

The user can then:
- Import their Excel model as a Brightway database
- Analyse activities in databases (for example look at inventories, calculate impacts using all Brightway-available impact assessment methods and carry out a contribution analysis)
- Export ready-for-report tables of life cycle inventories and results
- Export a wide selection of ready-for-report figures

Here is an overview of the repository structure and the notebooks it contains:

- `.venv/` is the local Python virtual environment created by `uv`.
- `functions/` contains various functions for importing databases, running analyses and creating visualisations. Set your project names, database names and input paths in `functions/utils.py` (see Step 3). The `fun_*.py` files provide supporting functions used by the notebooks and should not be changed by the user.
- `project/01_import_background/` contains one notebook per background database: ecoinvent, BAFU, EXIOBASE and BONSAI, plus a notebook for extra biosphere flows and iLUC. These notebooks can be run to import your background databases to Brightway.
- `project/02_import_foreground.ipynb` can be run to import your Excel model.
- `project/03_analysis.ipynb` explores databases and activities, calculates impacts and shows contribution results. `project/03_analysis_and_visualisation.ipynb` adds more detailed inventory, contribution and plotting views.
- `project/04_workflow_template.ipynb` provides a reusable sequence for selecting activities, calculating LCA scores and contributions, and plotting or saving results.
- `pyproject.toml` lists the project dependencies; `uv.lock` records their resolved versions.
- `.gitignore` list the files in this repository which should not be synced when you push or pull changes.

## What are the pre-requisites for using this template?

You need the following:
- An IDE for viewing and editing code. We recommend VS Code.
- Python 3.12 or newer for executing code.
- uv for creating a virtual environment.
- A GitHub account.
- Git for cloning the repository and pushing changes.
- Access to the background database files you plan to import, or ecoinvent login credentials if you use its online importer.
- An Excel foreground model to import, with its location set in `functions/utils.py`.

## Step 1: Create your repository

On GitHub, open this template repository, select **Use this template**, then select **Create a new repository**. Choose the account or organisation that will own your project (i.e. 20lca), enter your new repository name, choose its visibility (private or public), and select **Create repository**.

Your new repository starts with the files and folder structure in this template. Clone your new repository to your computer like this:

Open your terminal and navigate to the location where you want to keep this repository (it should be kept locally, i.e. not on OneDrive):

```bash
cd "your path here"
```

Then go to your new repository on GitHub and click on **Code** then click on SSH and copy the displayed URL.

Then in your terminal enter:

```bash
git clone "your copied URL here"
```

Then navigate to your new repository folder on your PC using:

```bash
cd "your repository path here"
```

Continue with Step 2 from that folder.

For more detail, see [GitHub's guide to creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

## Step 2: Create your virtual environment

Since the dependencies for this project is already defined in `pyproject.toml` and `uv.lock` you can simply run this (remember you need to be in your repository folder):

```bash
uv sync
```

This reads the `pyproject.toml` file, which defines the project dependencies, and the `uv.lock` file, which contains the exact versions of those dependencies. `uv` then creates a new virtual environment in the repository folder and installs the required packages.

To activate your virtual environment simply run this:

```powershell
.venv\Scripts\Activate.ps1
```

If you are using VS Code it should remember your selection of interpreter (or kernel for jupyter notebooks) (CTRL+SHIFT+P in VS Code to select) and you do not need to write this every time you open your project in VS Code.

## Step 3: Define the necessary parameters in utils.py

Open `functions/utils.py` and review the `Config` class. You only need to change settings that differ for your project or for the databases you choose to import:

1. **For every project:** Set `PROJECT_NAME` to your Brightway project name. Set `PROJECT_DIRECTORY_PATH` to the folder containing your Excel model and `PROJECT_EXPORTS_PATH` to the folder where you want exports to go. These paths are built from `ONEDRIVE_PATH` in the template; change that base path if your files are elsewhere, or set the individual paths directly.
2. **If importing ecoinvent online:** Set `ECOINVENT_USERNAME`, `ECOINVENT_PASSWORD`, `ECOINVENT_VERSION` and `ECOINVENT_SYSTEM_MODEL` for the release you have access to.
3. **If importing ecoinvent from downloaded files:** `ECOINVENT_VERSION`, `ECOINVENT_ECOSPOLD_FOLDER_NAME`, `ECOINVENT_ECOSPOLD_PATH` and `ECOINVENT_BIOSPHERE_PATH` are already configured for ecoinvent 3.12 and its current file locations. Leave them unchanged unless you use a different release.
4. **For other background databases, only if you use them:** The paths for BAFU (`BAFU_ECOSPOLD_PATH`, `BAFU_MAPPING_FILE_PATH`), EXIOBASE (`EXIOBASE_CSV_PATH`), BONSAI (`BONSAI_PATH`) and iLUC (`EXTRA_BIOSPHERE_PATH`, `ILUC_PATH`) are already configured for the current versions. Leave these paths, and the iLUC workbook and sheet names, unchanged unless you use different versions.

## Step 4: Install your selected background database(s)

Open the relevant notebook in `project/01_import_background/` and select your project's `.venv` as the notebook kernel. Run its cells in order, following the instructions and checking for unlinked exchanges before writing the database. You only need to run the notebooks for the background databases your project uses:

- `01_import_ecoinvent.ipynb` offers an online import using ecoinvent access details and an import from local EcoSpold files. Choose the option that matches your inputs.
- `02_import_bafu.ipynb`, `03_import_exiobase.ipynb` and `04_import_bonsai.ipynb` import their respective sources from the paths set in `functions/utils.py`.
- `05_import_iluc.ipynb` imports extra biosphere flows and iLUC data. Run it after importing the ecoinvent database to which it links, if your project needs iLUC.

After an import, check the notebook's final database listing to confirm the database is present in your Brightway project. Imported databases are stored in Brightway; you do not need to import them again each time you open the project.

## Step 5: Import your Excel model

Open `project/02_import_foreground.ipynb`. In the notebook, replace the example Excel filename (`BW_LCI_importer_template.xlsx`) with your model's filename. Check the background database names used in its matching cells and update them to the databases you imported in Step 4.

Run the cells in order. Review the unlinked exchanges shown before the `write_database()` cell, correct any missing or mismatched links, and then write the foreground database. Confirm that it appears in the final database listing.

## Step 6: Explore your Brightway databases and analyse results

Start with `project/03_analysis.ipynb` to browse databases and activities, inspect inventories, calculate impact scores and explore contributions. Use `project/03_analysis_and_visualisation.ipynb` for more detailed contribution views and plots.

For a repeatable analysis of selected activities, use `project/04_workflow_template.ipynb`. Update its activity selections and calculation settings for your model, then run the cells in order. Its optional save step writes tables and figures.