from __future__ import annotations

import ast
import csv
import html
import math
import re
from pathlib import Path

import numpy as np
from lxml import etree
from stats_arrays.distributions import (
    LognormalUncertainty,
    NormalUncertainty,
    TriangularUncertainty,
    UniformUncertainty,
    UndefinedUncertainty,
)

NAME_LOC_RE = re.compile(r"^(.*)\s+\{([^{}]+)\}\s*$")

def strip_location_from_name(name, current_location=None):
    """
    If name ends with ' {...}', strip this part and return (clean_name, location).
    Location from name overrides current_location if found.
    """
    if not name:
        return name, current_location
    m = NAME_LOC_RE.match(name)
    if not m:
        return name, current_location
    base, loc_str = m.groups()
    base = base.strip()
    loc = loc_str.strip()
    return base, (loc or current_location)

def get_first(elem, xpath):
    """Helper: return first match or None."""
    res = elem.xpath(xpath)
    return res[0] if res else None

def get_attr(elem, name, default=None):
    return elem.get(name) if elem is not None and elem.get(name) is not None else default


def build_reference_index(root_dir: Path):
    """
    First pass: for each dataset, find its main production exchange
    and build an index keyed by that exchange's 'number' (flow id).

    Returns: dict[flow_id] = {
        'activity_code': dataset_number,
        'name': clean_name,
        'reference product': clean_name,
        'location': location,
        'unit': unit,
    }
    """
    ref_index = {}

    for xml in root_dir.rglob("*.xml"):
        tree = etree.parse(str(xml))
        root = tree.getroot()

        dataset = get_first(root, '//*[local-name()="dataset"]')
        if dataset is None:
            continue

        PI = get_first(dataset, './/*[local-name()="processInformation"]')
        RF = get_first(PI, './/*[local-name()="referenceFunction"]') if PI is not None else None
        geo = get_first(PI, './/*[local-name()="geography"]') if PI is not None else None

        if RF is None:
            continue

        raw_name = get_attr(RF, "name", "") or ""
        unit = get_attr(RF, "unit", "")
        xml_location = get_attr(geo, "location", None) or "GLO"
        dataset_number = get_attr(dataset, "number", "")

        # Clean name and location
        clean_name, location = strip_location_from_name(raw_name, xml_location)

        # Find main production exchange (outputGroup == "0")
        flow_data = get_first(dataset, './/*[local-name()="flowData"]')
        prod_flow_id = None

        if flow_data is not None:
            for exc in flow_data.xpath('./*[local-name()="exchange"]'):
                og = get_first(exc, './*[local-name()="outputGroup"]')
                og_val = og.text.strip() if og is not None and og.text else None
                if og_val == "0":
                    prod_flow_id = get_attr(exc, "number", None)
                    if prod_flow_id:
                        break

        # Fallback: if we didn't find a production exchange number, use dataset number
        flow_id = prod_flow_id or dataset_number
        if not flow_id:
            continue

        ref_index[flow_id] = {
            "activity_code": dataset_number,
            "name": clean_name,
            "reference product": clean_name,
            "location": location,
            "unit": unit,
        }

    return ref_index

def person_label(person_elem):
    """Return a compact 'Name (email)' label from a <person> element."""
    if person_elem is None:
        return None
    name = (get_attr(person_elem, "name", "") or "").strip()
    email = (get_attr(person_elem, "email", "") or "").strip()
    if name and email:
        return f"{name} ({email})"
    elif name:
        return name
    elif email:
        return email
    return None


def clean_comment(text: str) -> str:
    if not text:
        return ""

    # Decode HTML entities like &#10;
    t = html.unescape(text)

    # Drop trailing "UUID: ..." noise, if present
    t = re.sub(r"UUID:.*$", "", t, flags=re.S)

    # Normalise line breaks and remove empty lines
    lines = [ln.strip() for ln in t.replace("\r\n", "\n").split("\n")]
    lines = [ln for ln in lines if ln]  # drop completely empty lines

    return "\n".join(lines)


def add_uncertainty_fields_from_ecospold1(exc_xml, data: dict) -> dict:
    """
    Mutates & returns `data` by adding Brightway-style uncertainty fields
    from an ecospold1 <exchange> element.
    """

    # ecoSpold1 uncertaintyType (0..4)
    try:
        uncertainty = int(exc_xml.get("uncertaintyType", 0))
    except ValueError:
        uncertainty = 0

    def floatish(x):
        if x is None:
            return np.nan
        try:
            return float(x.strip())
        except Exception:
            try:
                return float(x)
            except Exception:
                return np.nan

    mean = floatish(exc_xml.get("meanValue"))
    min_ = floatish(exc_xml.get("minValue"))
    max_ = floatish(exc_xml.get("maxValue"))
    sigma95 = floatish(exc_xml.get("standardDeviation95"))

    # Some data has nonsense lognormal parameters -> treat as undefined
    if uncertainty == 1 and (sigma95 in (0, 1) or np.isnan(sigma95)):
        uncertainty = 0

    # ---------- LOGNORMAL ----------
    if uncertainty == 1:
        # Guard against mean <= 0 explicitly; lognormal not defined there
        if mean == 0 or np.isnan(mean):
            data.update(
                {
                    "uncertainty type": UndefinedUncertainty.id,
                    "amount": float(mean),
                    "loc": float(mean),
                }
            )
            return data

        # Normal lognormal case
        data.update(
            {
                "uncertainty type": LognormalUncertainty.id,  # ID 2
                "amount": float(mean),
                "loc": math.log(abs(mean)),
                "scale": math.log(math.sqrt(float(sigma95))),
                "negative": mean < 0,
            }
        )

        # Extra sanity check: bad scale -> fall back to undefined
        if np.isnan(data["scale"]):
            data["uncertainty type"] = UndefinedUncertainty.id
            data["loc"] = data["amount"]
            data.pop("scale", None)

        return data

    # ---------- NORMAL ----------
    if uncertainty == 2:
        data.update(
            {
                "uncertainty type": NormalUncertainty.id,  # ID 3
                "amount": float(mean),
                "loc": float(mean),
                "scale": float(sigma95) / 2.0,
            }
        )
        return data

    # ---------- TRIANGULAR ----------
    if uncertainty == 3:
        data.update(
            {
                "uncertainty type": TriangularUncertainty.id,  # ID 5
                "minimum": float(min_),
                "maximum": float(max_),
            }
        )
        most_likely = floatish(exc_xml.get("mostLikelyValue"))
        if not np.isnan(most_likely):
            data["amount"] = data["loc"] = most_likely
        else:
            data["amount"] = data["loc"] = float(mean)
        return data

    # ---------- UNIFORM ----------
    if uncertainty == 4:
        data.update(
            {
                "uncertainty type": UniformUncertainty.id,  # ID 4
                "amount": float(mean),
                "minimum": float(min_),
                "maximum": float(max_),
            }
        )
        return data

    # ---------- UNDEFINED / NO UNCERTAINTY ----------
    data.update(
        {
            "uncertainty type": UndefinedUncertainty.id,  # ID 0
            "amount": float(mean),
            "loc": float(mean),
        }
    )
    return data

UNITS_MAP = {
    'kg': 'kilogram',
    'tkm': 'ton kilometer',
    'p': 'unit',
    'kWh': 'kilowatt hour',
    'MJ': 'megajoule',
    'm2': 'square meter',
    'm': 'meter',
    'Nm3': 'cubic meter',
    'km': 'kilometer',
    'personkm': 'person-kilometer',
    'my': 'meter-year',
    'unit': 'unit',
    'm3': 'cubic meter',
    'm2a': 'square meter-year',
    'kmy': 'kilometer-year',
    'a': 'year',
    'm3y': 'cubic meter-year',
    'kBq': 'kilo Becquerel',
    'ha': 'hectare',
    'Bq': 'Becquerel',
    'hr': 'hour'
}

CATS_MAP = {
    ('emissions to air', 'unspecified'): ('air',),
    ('emissions to air', 'high. pop.'): ('air', 'urban air close to ground'),
    ('emissions to air', 'low. pop.'): ('air', 'non-urban air or from high stacks'),
    ('emissions to air', 'stratosphere + troposphere'): ('air', 'lower stratosphere + upper troposphere'),
    ('emissions to air', 'low. pop., long-term'): ('air', 'low population density, long-term'),
    ('emissions to air', 'indoor'): ('air', 'urban air close to ground'),
    
    ('emissions to soil', 'unspecified'): ('soil',),
    ('emissions to soil', 'forestry'): ('soil', 'forestry'),
    ('emissions to soil', 'agricultural'): ('soil', 'agricultural'),
    ('emissions to soil', 'industrial'): ('soil', 'industrial'),
    
    ('emissions to water', 'ocean'): ('water', 'ocean'),
    ('emissions to water', 'river'): ('water', 'surface water'),
    ('emissions to water', 'unspecified'): ('water',),
    ('emissions to water', 'groundwater, long-term'): ('water', 'ground-, long-term'),
    ('emissions to water', 'groundwater'): ('water', 'ground-'),
    ('emissions to water', 'lake'): ('water', 'surface water'),
    ('emissions to water', 'river, long-term'): ('water', 'surface water'),
    ('emissions to water', 'fossilwater'): ('water', 'fossil well'),
    
    ('economic issues', 'unspecified'): ('economic', 'primary production factor'),

    ('resources', 'in ground'): ('natural resource', 'in ground'),
    ('resources', 'land'): ('natural resource', 'land'),
    ('resources', 'in water'): ('natural resource', 'in water'),
    ('resources', 'in air'): ('natural resource', 'in air'),
    ('resources', 'biotic'): ('natural resource', 'biotic'),
}

def parse_ecospold_file(xml_path: Path, db_name: str, ref_index: dict):
    """Parse a single ecoSpold1 file into a Brightway-like dict, using ref_index."""
    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    dataset = get_first(root, '//*[local-name()="dataset"]')
    if dataset is None:
        return None

    PI = get_first(dataset, './/*[local-name()="processInformation"]')
    RF = get_first(PI, './/*[local-name()="referenceFunction"]') if PI is not None else None
    geo = get_first(PI, './/*[local-name()="geography"]') if PI is not None else None
    TP = get_first(PI, './/*[local-name()="timePeriod"]') if PI is not None else None

    if RF is None:
        return None

    # Basic fields
    raw_name = get_attr(RF, "name", "") or ""
    unit = UNITS_MAP.get(get_attr(RF, "unit", ""))
    xml_location = get_attr(geo, "location", None) or "GLO"
    dataset_number = get_attr(dataset, "number", "")

    # Clean activity name and location (strip trailing {LOC})
    name, location = strip_location_from_name(raw_name, xml_location)
    ref_product = name

    # Build comment from various ecoSpold1 fields, then clean it
        # --- Build enriched comment from RF + timePeriod + metaInformation ---

    rf_comment = get_attr(RF, "generalComment", "") or ""

    # Time period: text + explicit start/end dates if present
    tp_text = get_attr(TP, "text", "") or ""
    tp_start_elem = get_first(TP, './/*[local-name()="startDate"]') if TP is not None else None
    tp_end_elem = get_first(TP, './/*[local-name()="endDate"]') if TP is not None else None
    tp_start = (tp_start_elem.text or "").strip() if tp_start_elem is not None and tp_start_elem.text else ""
    tp_end = (tp_end_elem.text or "").strip() if tp_end_elem is not None and tp_end_elem.text else ""

    time_lines = []
    if tp_text:
        time_lines.append(f"Time period: {tp_text}")
    if tp_start or tp_end:
        if tp_start and tp_end:
            time_lines.append(f"Time period (data): {tp_start} – {tp_end}")
        elif tp_start:
            time_lines.append(f"Time period (data): from {tp_start}")
        elif tp_end:
            time_lines.append(f"Time period (data): until {tp_end}")

    # Geography line: location + textual description if any
    geo_text = get_attr(geo, "text", "") or ""
    geo_lines = []
    if xml_location or geo_text:
        if geo_text:
            geo_lines.append(f"Geography: {xml_location} – {geo_text}")
        else:
            geo_lines.append(f"Geography: {xml_location}")

    # Technology description
    tech = get_first(PI, './/*[local-name()="technology"]') if PI is not None else None
    tech_text = get_attr(tech, "text", "") or ""
    tech_lines = []
    if tech_text:
        tech_lines.append(f"Technology: {tech_text}")

    # metaInformation (administrative + modelling & validation)
    MI = get_first(dataset, './/*[local-name()="metaInformation"]')
    AI = get_first(MI, './/*[local-name()="administrativeInformation"]') if MI is not None else None
    MV = get_first(MI, './/*[local-name()="modellingAndValidation"]') if MI is not None else None

    meta_lines = []

    # --- Representativeness & production volume ---
    rep = get_first(MV, './/*[local-name()="representativeness"]') if MV is not None else None
    if rep is not None:
        rep_parts = []

        # some schemas use e.g. "productionVolume", others "productionVolumeText"
        prod_vol = get_attr(rep, "productionVolume", "") or ""
        sampling = get_attr(rep, "samplingProcedure", "") or ""
        extrap = get_attr(rep, "extrapolations", "") or ""
        unc_adj = get_attr(rep, "uncertaintyAdjustments", "") or ""

        if prod_vol and prod_vol.lower() != "na":
            rep_parts.append(f"Production volume: {prod_vol}")
        if sampling and sampling.lower() != "<null>":
            rep_parts.append(f"Sampling: {sampling}")
        if extrap and extrap.lower() != "<null>":
            rep_parts.append(f"Extrapolations: {extrap}")
        if unc_adj and unc_adj.lower() != "none":
            rep_parts.append(f"Uncertainty adjustments: {unc_adj}")

        if rep_parts:
            meta_lines.append("Representativeness: " + "; ".join(rep_parts))

    # --- People: build index of persons in this dataset ---
    persons = {}
    if AI is not None:
        for p in AI.xpath('.//*[local-name()="person"]'):
            num = get_attr(p, "number", None)
            if num:
                persons[num] = p

        # Data entry person
        de = get_first(AI, './/*[local-name()="dataEntryBy"]')
        de_num = get_attr(de, "person", None) if de is not None else None
        de_label = person_label(persons.get(de_num))
        if de_label:
            meta_lines.append(f"Data entry: {de_label}")

        # Data generator
        dgp = get_first(AI, './/*[local-name()="dataGeneratorAndPublication"]')
        dgp_num = get_attr(dgp, "person", None) if dgp is not None else None
        dgp_label = person_label(persons.get(dgp_num))
        if dgp_label:
            meta_lines.append(f"Data generator: {dgp_label}")

    # --- Validation info ---
    if MV is not None:
        val = get_first(MV, './/*[local-name()="validation"]')
        if val is not None:
            details = get_attr(val, "proofReadingDetails", "") or ""
            validator_num = get_attr(val, "proofReadingValidator", None)
            validator_label = person_label(persons.get(validator_num)) if validator_num else None

            if validator_label:
                meta_lines.append(f"Proof-reading validator: {validator_label}")
            if details:
                meta_lines.append(f"Validation details: {details}")

    # --- Source / publication info ---
    if MV is not None:
        src = get_first(MV, './/*[local-name()="source"]')
        if src is not None:
            first_author = get_attr(src, "firstAuthor", "") or ""
            add_authors = get_attr(src, "additionalAuthors", "") or ""
            year = get_attr(src, "year", "") or ""
            title = get_attr(src, "title", "") or ""
            publisher = get_attr(src, "publisher", "") or ""
            place = get_attr(src, "placeOfPublications", "") or ""
            volume = get_attr(src, "volumeNo", "") or ""

            src_parts = []
            if first_author:
                src_parts.append(first_author)
            if add_authors:
                # compress "Frischknecht R., Stolz P." instead of listing everything verbosely
                src_parts.append(add_authors)
            if year:
                src_parts.append(f"({year})")
            if title:
                src_parts.append(title)
            if publisher or place or volume:
                pub_bits = ", ".join(
                    [x for x in [publisher, place, f"vol. {volume}" if volume else ""] if x]
                )
                if pub_bits:
                    src_parts.append(pub_bits)

            if src_parts:
                meta_lines.append("Source: " + " ".join(src_parts))

    # --- Combine everything and clean it ---
    comment_sections = []

    if rf_comment:
        comment_sections.append(rf_comment)

    comment_sections.extend(time_lines)
    comment_sections.extend(geo_lines)
    comment_sections.extend(tech_lines)
    comment_sections.extend(meta_lines)

    comment = clean_comment("\n".join(cs for cs in comment_sections if cs))


    # Simple classifications
    category = get_attr(RF, "category", None)
    subcategory = get_attr(RF, "subCategory", None)
    classifications = []
    if category or subcategory:
        classifications.append(
            ("EcoSpold01Categories", f"{category or ''}/{subcategory or ''}")
        )

    # Exchanges
    flow_data = get_first(dataset, './/*[local-name()="flowData"]')
    exchanges = []

    if flow_data is not None:
        for exc in flow_data.xpath('./*[local-name()="exchange"]'):
            # We still require a numeric meanValue; skip if missing
            mean_value = get_attr(exc, "meanValue", None)
            if mean_value is None:
                continue

            raw_ex_name = get_attr(exc, "name", "") or ""
            ex_unit = UNITS_MAP.get(get_attr(exc, "unit", ""))
            ex_cat = get_attr(exc, "category", "")
            ex_subcat = get_attr(exc, "subCategory", "")
            ex_loc_xml = get_attr(exc, "location", None)

            # Strip location from exchange name
            ex_name, ex_loc_from_name = strip_location_from_name(raw_ex_name, ex_loc_xml)
            ex_loc = ex_loc_from_name

            og = get_first(exc, './*[local-name()="outputGroup"]')
            ig = get_first(exc, './*[local-name()="inputGroup"]')
            og_val = og.text.strip() if og is not None and og.text else None
            ig_val = ig.text.strip() if ig is not None and ig.text else None

            ex_cat_lower = (ex_cat or "").lower()
            ex_subcat_lower = (ex_subcat or "").lower()
            
            # Heuristics for biosphere categories
            is_biosphere_category = (
                ex_cat_lower.startswith("emissions to ")
                or ex_cat_lower.startswith("emission to ")
                or ex_cat_lower in {"emissions", "emission"}
                or "resource" in ex_cat_lower
                or (ex_cat, ex_subcat) in CATS_MAP
            )
            
            # Lithium case: category 'resources', subcategory 'in ground'
            # will satisfy "resource" in ex_cat_lower and be biosphere.
            
            if og_val == "0":
                ex_type = "production"
            elif is_biosphere_category:
                ex_type = "biosphere"
            elif ig_val is not None:
                ex_type = "technosphere"
            else:
                # Fallback: if we have no input group and no explicit biosphere category,
                # treat it as biosphere (this will catch odd emissions that lack inputGroup)
                ex_type = "biosphere"


            exc_dict = {
                "name": ex_name,
                "unit": ex_unit,
                "type": ex_type,
                "categories": CATS_MAP.get((ex_cat, ex_subcat), (ex_cat, ex_subcat)),
            }

            if ex_loc:
                exc_dict["location"] = ex_loc

            # Optional per-exchange comment (also cleaned a bit)
            ex_comment = exc.get("generalComment")
            if ex_comment:
                exc_dict["comment"] = clean_comment(ex_comment)

            ex_number = get_attr(exc, "number", None)
            if ex_number:
                exc_dict["flow"] = ex_number

                # Inject reference product from the producer, if known
                if ex_type in ("technosphere", "production"):
                    ref_info = ref_index.get(ex_number)
                    if ref_info is not None:
                        exc_dict["reference product"] = ref_info["reference product"]
                        if "location" not in exc_dict or not exc_dict["location"]:
                            exc_dict["location"] = ref_info["location"]

            # Add Brightway-style uncertainty parameters
            add_uncertainty_fields_from_ecospold1(exc, exc_dict)

            exchanges.append(exc_dict)

    data = {
        "database": db_name,
        "code": dataset_number,
        "name": name,
        "reference product": ref_product,
        "location": location,
        "unit": unit,
        "comment": comment,
        "classifications": classifications,
        "exchanges": exchanges,
        "filename": xml_path.name,
        "type": "process",
    }

    return data

def parse_category(cat_str):
    cat_str = (cat_str or "").strip()
    if not cat_str:
        return None
    return tuple(ast.literal_eval(cat_str))


def load_bafu_ecospold(ecospold_dir: Path, db_name: str) -> list[dict]:
    """Parse all BAFU EcoSpold 1 XML files into Brightway-style datasets.

    Parameters
    ----------
    ecospold_dir:
        Directory containing the BAFU EcoSpold 1 ``.xml`` files.
    db_name:
        Name that the BAFU database will have in Brightway.

    Returns
    -------
    list[dict]
        Dataset dictionaries ready to be assigned to a Brightway LCI importer.
    """
    ecospold_dir = Path(ecospold_dir)
    if not ecospold_dir.is_dir():
        raise FileNotFoundError(f"BAFU EcoSpold directory not found: {ecospold_dir}")

    ref_index = build_reference_index(ecospold_dir)
    print(f"Reference index contains {len(ref_index)} entries.")

    all_data = []
    for xml in ecospold_dir.rglob("*.xml"):
        dataset = parse_ecospold_file(xml, db_name, ref_index)
        if dataset is not None:
            all_data.append(dataset)

    print(f"Built {len(all_data)} dataset dictionaries.")
    return all_data


def load_elementary_flow_mapping(csv_path: Path) -> dict:
    """Load the BAFU-to-ecoinvent elementary-flow mapping CSV."""
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"BAFU mapping file not found: {csv_path}")

    mapping = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        # Fix BOM in header if present
        if reader.fieldnames:
            reader.fieldnames = [fn.lstrip("\ufeff") for fn in reader.fieldnames]

        for row in reader:
            bafu_name = row["BAFU name"].strip()
            bafu_cat = parse_category(row["BAFU category"])
            key = (bafu_name, bafu_cat)

            mapping[key] = {
                "ecoinvent_name": (row.get("Ecoinvent name") or "").strip() or None,
                "ecoinvent_category": parse_category(row.get("Ecoinvent category")),
            }

    print(f"{len(mapping)} elementary-flow mapping entries loaded.")
    return mapping


def apply_elementary_flow_mapping(all_data: list[dict], mapping: dict) -> list[dict]:
    """Apply the BAFU-to-ecoinvent mapping to biosphere exchanges in-place."""
    mapped = 0
    for dataset in all_data:
        for exchange in dataset["exchanges"]:
            if exchange["type"] != "biosphere":
                continue

            key = (exchange["name"], exchange["categories"])
            if key not in mapping:
                continue

            new_name = mapping[key]["ecoinvent_name"]
            new_category = mapping[key]["ecoinvent_category"]

            if new_name:
                exchange["name"] = new_name
            if new_category:
                exchange["categories"] = new_category
            mapped += 1

    print(f"Applied elementary-flow mapping to {mapped} biosphere exchanges.")
    return all_data
