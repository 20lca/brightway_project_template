"""Helper strategies used when importing EXIOBASE from a SimaPro CSV export."""

import logging
import re


def remove_curly_content(text: str) -> str:
    """Remove text in curly brackets from a name."""
    return re.sub(r"{[^}]*}", "", text).replace("  ", " ").strip()


def get_location_from_substring(text: str) -> str:
    """Extract a location from ``{...}``; use ``GLO`` if none is present."""
    match = re.search(r"{(.*?)}", text)
    if match is not None:
        return match[1]

    logging.warning(
        "Could not identify the location of '%s'. GLO location is assigned.",
        text,
    )
    return "GLO"


def get_location_from_name(data: list) -> list:
    """Add activity and technosphere/production locations from names."""
    for dataset in data:
        if dataset.get("location") is None:
            dataset["location"] = get_location_from_substring(dataset["name"])

        for exchange in dataset.get("exchanges", []):
            if exchange.get("location") is not None:
                continue
            if exchange["type"] in {"technosphere", "production"}:
                exchange["location"] = get_location_from_substring(exchange["name"])

    return data


def remove_location_from_name(data: list) -> list:
    """Remove ``{location}`` text after the location has been stored separately."""
    for dataset in data:
        dataset["name"] = remove_curly_content(dataset["name"])

        for exchange in dataset.get("exchanges", []):
            if exchange["type"] in {"technosphere", "production"}:
                exchange["name"] = remove_curly_content(exchange["name"])

    return data


def remove_old_ef(data: list) -> list:
    """Remove outdated CO2-equivalent biosphere flows from the SimaPro export."""
    for dataset in data:
        if "exchanges" not in dataset:
            continue

        dataset["exchanges"] = [
            exchange
            for exchange in dataset["exchanges"]
            if not (
                exchange["type"] == "biosphere"
                and exchange["name"].startswith("CO2-eq (")
            )
        ]

    return data


def production_as_datasetname(data: list) -> list:
    """Set each production exchange name equal to its dataset name."""
    for dataset in data:
        for exchange in dataset.get("exchanges", []):
            if exchange["type"] == "production":
                exchange["name"] = dataset["name"]

    return data


def remove_empty_activities(data: list) -> list:
    """Remove empty activities and exchanges pointing to them."""
    empty_activities = {
        dataset["name"]
        for dataset in data
        if "exchanges" not in dataset and dataset["type"] != "product"
    }

    for dataset in data:
        if dataset["type"] == "product" or dataset["name"] in empty_activities:
            continue

        dataset["exchanges"] = [
            exchange
            for exchange in dataset["exchanges"]
            if exchange["name"] not in empty_activities
        ]

    return [
        dataset
        for dataset in data
        if "exchanges" in dataset or dataset["type"] == "product"
    ]


def tweak3(data: list) -> list:
    """Adapt selected EXIOBASE biosphere flows to match ``biosphere3``."""
    for dataset in data:
        for exchange in dataset.get("exchanges", []):
            if (
                exchange["name"] == "Carbon dioxide, in air"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["categories"] = ("natural resource", "in air")

            elif (
                exchange["name"] == "Oxygen"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["categories"] = ("air",)

            elif exchange["name"] == "Water, unspecified natural origin/kg":
                exchange["name"] = "Water, unspecified natural origin"
                exchange["amount"] /= 1000
                exchange["unit"] = "cubic meter"
                exchange["categories"] = ("natural resource", "in water")

            elif exchange["name"] == "Carbon monoxide":
                exchange["name"] = "Carbon monoxide, fossil"

            elif (
                exchange["name"] == "Occupation, arable land, unspecified use"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["categories"] = ("natural resource", "land")
                exchange["amount"] *= 10000
                exchange["unit"] = "square meter-year"

            elif (
                exchange["name"] == "Occupation, forest, unspecified"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["categories"] = ("natural resource", "land")
                exchange["amount"] *= 10000
                exchange["unit"] = "square meter-year"

            elif (
                exchange["name"] == "Occupation, grassland"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["name"] = (
                    "Occupation, grassland, natural, for livestock grazing"
                )
                exchange["categories"] = ("natural resource", "land")
                exchange["amount"] *= 10000
                exchange["unit"] = "square meter-year"

            elif (
                exchange["name"] == "Occupation, urban, continuously built"
                and exchange["categories"] == ("natural resource",)
            ):
                exchange["categories"] = ("natural resource", "land")
                exchange["amount"] *= 10000
                exchange["unit"] = "square meter-year"

    return data
