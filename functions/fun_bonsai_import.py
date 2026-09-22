import json
from pathlib import Path

import bw2data as bd

from functions.utils import Config


def define_b3_map(bonsai_path: Path | None = None) -> dict[str, str]:
    """Map BONSAI elementary-flow codes to the active Brightway biosphere.

    BONSAI metadata records the corresponding Brightway flow UUID in
    ``source_id``. Only mappings whose target exists in the active biosphere
    database are returned; the importer creates its supplementary biosphere
    database for the remaining flows.
    """

    path = Path(bonsai_path or Config.BONSAI_PATH)
    with (path / "io_metadata.json").open(encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    biosphere_codes = {
        flow["code"] for flow in bd.Database(bd.config.biosphere)
    }

    return {
        bonsai_code: flow_metadata["source_id"]
        for bonsai_code, flow_metadata in metadata.items()
        if flow_metadata.get("source_id") in biosphere_codes
    }
