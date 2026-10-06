"""Find company shared folders users configure paths only in utils.py."""

import os
from pathlib import Path


class _UnresolvedFolder(os.PathLike):
    """Defer the setup error until a workflow actually uses this folder."""

    def __init__(self, message):
        self.message = message

    def __truediv__(self, part):
        return self

    def __fspath__(self):
        raise FileNotFoundError(self.message)

    def __str__(self):
        raise FileNotFoundError(self.message)

    def is_dir(self):
        raise FileNotFoundError(self.message)

    def is_file(self):
        raise FileNotFoundError(self.message)


def _find_folder(names, setting, label):
    roots = [
        Path.home() / "OneDrive - 2.-0 LCA Consultants ApS",
        Path.home() / "2.-0 LCA Consultants ApS",
    ]
    for variable in ("OneDriveCommercial", "OneDrive"):
        if os.environ.get(variable):
            roots.append(Path(os.environ[variable]))

    matches = {}
    for root in roots:
        for name in names:
            candidate = root / name
            if candidate.is_dir():
                # The environment and home directory may identify the same folder.
                matches.setdefault(candidate.resolve(), candidate)
    if len(matches) == 1:
        return next(iter(matches.values()))

    reason = f"Could not find your {label} folder automatically."
    if matches:
        reason = f"Found more than one {label} folder:\n" + "\n".join(map(str, matches.values()))
    return _UnresolvedFolder(
        f'{reason}\nSet {setting} in functions/utils.py to '
        f'Path(r"your folder here"). Copy its location from File Explorer, '
        'then restart the notebook kernel.'
    )


def find_databases_folder():
    """Recognise the company's shortcut and library sync folder names."""
    return _find_folder(
        ("Databases", "Intranet - Databases", " Intranet - Databases Databases",
         "Intranet - Databases Databases"),
        "DATABASES_PATH", "shared Databases",
    )
