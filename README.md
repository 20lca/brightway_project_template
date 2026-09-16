# brightway_project_template
First draft of a repository for starting new brightway project.

## Virtual environment

To create a virtual environment using `uv`, go to the repository folder and run:

```bash
uv sync
```

This reads the `pyproject.toml` file, which defines the project dependencies, and the `uv.lock` file, which contains the exact versions of those dependencies. `uv` then creates a new virtual environment in the repository folder and installs the required packages.
