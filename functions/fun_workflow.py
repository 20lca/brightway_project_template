"""Reusable workflow based on the supplied brightway_template_analysis notebook.

multi_category_score_table retains the scoring function supplied in that archive
(attributed there to SUPERVAL). Contributions use Brightway LCA scores and
characterized process biosphere flows. Plotting reuses fun_visualisation.
All calculations are for one reference-product unit.
"""
import pandas as pd
import numpy as np
from bw2data import get_activity
from functions.fun_visualisation import plot_contribution_bar


def validate_selection(activities, categories):
    """Require activities and one method per category; never sum impact methods."""
    if not activities or not categories:
        raise ValueError("Select at least one activity and one impact category.")
    for label, info in categories.items():
        if len(info["methods"]) != 1:
            raise ValueError(f"{label}: select exactly one method per category.")


def multi_category_score_table(activities: dict, categories) -> pd.DataFrame:
    """Source scoring function with selection validation; scores per one unit."""
    validate_selection(activities, categories)
    rows = []
    for name, activity in activities.items():
        for category_key, info in categories.items():
            rows.append({
                "Process": name,
                "Activity Name": activity.get("name"),
                "Location": activity.get("location"),
                "Functional Unit": activity.get("unit"),
                "Category": f"{info['label']} ({info['unit']})",
                "Score": sum(activity.lca(m).score for m in info["methods"]),
            })
    return pd.DataFrame(rows)


def calculate_contributions(activities, categories, *, cutoff=0.005):
    """Return totals, retained first-tier inputs, direct flows, and cutoff remainders.

    Direct biosphere flows are never filtered. Other contains only inputs omitted
    by cutoff, relative to the absolute net total. Zero-total shares are undefined.
    """
    validate_selection(activities, categories)
    if not 0 <= cutoff < 1:
        raise ValueError("cutoff must be at least zero and less than one.")
    tables = {}
    for label, activity in activities.items():
        for category, info in categories.items():
            lca = activity.lca(info["methods"][0])
            total = float(lca.score)
            column = lca.dicts.activity[activity.id]
            production = list(activity.production())
            if len(production) > 1:
                raise ValueError(f"Expected at most one production exchange for {label}.")
            production_amount = float(lca.technosphere_matrix[
                lca.dicts.product[production[0].input.id], column
            ]) if production else 1.0
            if production_amount == 0:
                raise ValueError(f"Zero net production for {label}.")

            def row(name, score, kind, branch, *, amount=None, node=None):
                return {
                    "label": branch, "parent": None if kind == "Total" else "root",
                    "score": score, "fraction": score / total if total else None,
                    "amount": amount, "name": name,
                    "key": node.key if node is not None else None,
                    "location": node.get("location") if node is not None else None,
                    "unit": node.get("unit") if node is not None else None,
                    "contribution_type": kind,
                }

            rows = [row(activity.get("name", label), total, "Total", "root",
                        amount=1.0, node=activity)]
            # Scale the process column by net production, not total supply:
            # upstream returns to this process are already in input scores.
            biosphere = lca.biosphere_matrix[:, column] / production_amount
            direct = (lca.characterization_matrix @ biosphere).tocoo()
            direct.sum_duplicates()
            for flow_index, score in zip(direct.row, direct.data):
                if score == 0:
                    continue
                flow = get_activity(lca.dicts.biosphere.reversed[int(flow_index)])
                compartments = ", ".join(flow.get("categories", ()))
                name = flow.get("name", "(Unknown flow)")
                if compartments:
                    name += f" ({compartments})"
                rows.append(row(name, float(score), "Direct", f"direct_{flow_index}",
                                amount=float(biosphere[flow_index, 0]), node=flow))

            omitted = []
            for index, exchange in enumerate(activity.technosphere()):
                if exchange.input.id == exchange.output.id:
                    continue
                amount = float(exchange["amount"]) / production_amount
                lca.redo_lcia({exchange.input.id: amount})
                score = float(lca.score)
                if abs(score) <= abs(total * cutoff):
                    omitted.append(score)
                else:
                    rows.append(row(exchange.input.get("name", "(Unknown name)"),
                                    score, "Input", f"input_{index}",
                                    amount=amount, node=exchange.input))
            rows.append(row("other", float(sum(omitted)), "Other", "other"))
            subtotal = sum(item["score"] for item in rows[1:])
            if not np.isclose(subtotal, total, rtol=1e-7, atol=1e-12):
                raise ValueError(
                    f"Contribution breakdown does not reconcile for {label}, {category}: "
                    f"total={total}, breakdown={subtotal}. Check production and exchanges."
                )
            tables[(label, category)] = pd.DataFrame(rows)
    return tables


def combine_contributions(tables, activities, categories):
    """Combine copies of contribution tables with selection metadata."""
    parts = [
        table.assign(
            activity_label=label, category_key=category,
            method_unit=categories[category]["unit"],
            reference_amount=1, reference_unit=activities[label]["unit"],
        )
        for (label, category), table in tables.items()
    ]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def check_contribution_scores(scores, tables, categories):
    """Check that every recursive root agrees with its independently calculated score."""
    rows = []
    for (label, category), table in tables.items():
        info = categories[category]
        category_label = f"{info['label']} ({info['unit']})"
        selected = scores.loc[
            (scores["Process"] == label) & (scores["Category"] == category_label),
            "Score",
        ]
        roots = table.loc[table["parent"].isna(), "score"]
        if len(selected) != 1 or len(roots) != 1:
            raise ValueError(f"Expected one total and one root for {label}, {category}.")
        total, root = float(selected.iloc[0]), float(roots.iloc[0])
        rows.append({
            "Process": label, "Category": category, "Score": total,
            "Recursive root": root,
            "Matches": bool(np.isclose(total, root, rtol=1e-7, atol=1e-12)),
        })
    return pd.DataFrame(rows)


def plot_workflow_contributions(tables, activities, categories, *, top_n=15):
    """Plot stored first-tier tables with existing 2-0 styling; return figures.

    Internal branch IDs keep bars separate; visible labels show activity names only.
    No LCA calculations occur here. Empty child tables are skipped explicitly.
    """
    figures = {}
    for (label, category), table in tables.items():
        children = table.loc[table["parent"].notna()].copy()
        if children.empty:
            print(f"No retained first-tier inputs: {label} | {category}")
            continue
        children = children.reset_index(drop=True)
        display_names = children["name"].copy()
        children["name"] = [f"branch_{i}" for i in children.index]
        order = children["score"].abs().sort_values(ascending=False).index[:top_n]
        activity, info = activities[label], categories[category]
        fig, ax = plot_contribution_bar(
            children, parent_column=None, top_n=top_n,
            title=f"{activity['name']} - {info['label']}",
            unit=f"{info['unit']}",
            figsize=(9, max(3, 0.35 * min(len(children), top_n))),
            show=False,
        )
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(display_names.loc[order].tolist())
        ax.title.set_fontsize(11)
        ax.tick_params(axis="y", labelsize=8)
        ax.tick_params(axis="x", labelsize=8)
        fig.tight_layout()
        figures[(label, category)] = fig
    return figures
