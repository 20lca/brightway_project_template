import bw2data as bd


def define_b3_map() -> dict:
    """Create the BONSAI-to-biosphere3 flow mapping required by BonsaiImporter."""

    biosphere_db = bd.Database(bd.config.biosphere)

    co_fossil = biosphere_db.get(
        name="Carbon monoxide, fossil",
        categories=("air",),
    )
    co2_non_fossil = biosphere_db.get(
        name="Carbon dioxide, non-fossil",
        categories=("air",),
    )
    co2_fossil = biosphere_db.get(
        name="Carbon dioxide, fossil",
        categories=("air",),
    )
    ch4_fossil = biosphere_db.get(
        name="Methane, fossil",
        categories=("air",),
    )
    ch4_non_fossil = biosphere_db.get(
        name="Methane, non-fossil",
        categories=("air",),
    )
    n2o = biosphere_db.get(
        name="Dinitrogen monoxide",
        categories=("air",),
    )

    return {
        "Carbon_dioxide__fossil_Air": co2_fossil["code"],
        "Carbon_dioxide__biogenic_Air": co2_non_fossil["code"],
        "Methane__fossil_Air": ch4_fossil["code"],
        "Methane__biogenic_Air": ch4_non_fossil["code"],
        "Carbon_monoxide__fossil_Air": co2_non_fossil["code"],
        "Dinitrogen_monoxide_Air": n2o["code"],
    }