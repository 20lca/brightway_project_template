"""Excel report export styled after Report example, AAK.dotx.

Reference: TableGrid headers #6DAACB, white text; body TT Commons Pro,
9 pt, #353B37; section rows #BFD2D0; thin table rules.
The style is embedded so exporting does not require the Word template.
"""
from math import ceil
from numbers import Real

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER = "6DAACB"
SECTION = "BFD2D0"
TEXT = "353B37"
FONT = "TT Commons Pro"


def _value(value):
    if isinstance(value, (tuple, list, dict)):
        return str(value)
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def _row(ws, values, *, header=False, section=False):
    ws.append([_value(value) for value in values])
    row = ws.max_row
    for cell in ws[row]:
        # Labels from databases are text, even if they begin with "=".
        if isinstance(cell.value, str):
            cell.data_type = "s"
        cell.font = Font(name=FONT, size=9, bold=header or section,
                         color="FFFFFF" if header else TEXT)
        cell.fill = PatternFill("solid", fgColor=HEADER if header else SECTION if section else "FFFFFF")
        cell.alignment = Alignment(vertical="top", wrap_text=True,
                                   horizontal="right" if isinstance(cell.value, Real) and not isinstance(cell.value, bool) else "left")
        cell.border = Border(bottom=Side(style="thin", color=TEXT))
        if isinstance(cell.value, Real) and not isinstance(cell.value, bool):
            cell.number_format = "0" if isinstance(cell.value, int) else "0.000E+00"
    return row


def _finish(ws, *, filter_rows=True):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"
    for column in ws.columns:
        longest = max(len(str(cell.value or "")) for cell in column)
        width = min(48, max(14, longest + 3))
        ws.column_dimensions[column[0].column_letter].width = width
    for row in ws:
        lines = max(
            sum(max(1, ceil(len(line) / max(1, ws.column_dimensions[get_column_letter(c.column)].width - 3)))
                for line in str(c.value or "").split("\n"))
            for c in row
        )
        ws.row_dimensions[row[0].row].height = max(20, lines * 13 + 6)
    if filter_rows:
        ws.auto_filter.ref = ws.dimensions
    ws.print_title_rows = "1:1"
    ws.print_options.horizontalCentered = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3 if ws.max_column > 10 else ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_area = ws.dimensions


def _table(wb, name, frame):
    ws = wb.create_sheet(name)
    _row(ws, list(frame.columns), header=True)
    for values in frame.itertuples(index=False, name=None):
        _row(ws, values)
    for index, name in enumerate(frame.columns, 1):
        if str(name).lower() == "fraction":
            for row in range(2, ws.max_row + 1):
                ws.cell(row, index).number_format = "0.0%"
    _finish(ws)
    return ws


def export_workflow_excel(path, *, activity_selection, scores, scores_wide,
                          contributions, score_checks):
    """Export existing analysis tables; preserve values and all retained branches.

    Contribution overview has green section rows and marked total rows.
    Contributions data remains flat and filterable, including every raw column.
    This exports existing calculations, not a newly calculated LCI.
    """
    wb = Workbook()
    wb.remove(wb.active)
    _table(wb, "Activities", activity_selection)
    _table(wb, "LCA overview", scores_wide)
    _table(wb, "LCA scores", scores)
    ws = wb.create_sheet("Contribution overview")
    columns = [c for c in ("name", "location", "amount", "score", "fraction") if c in contributions]
    labels = {"name": "Contributor", "location": "Location", "amount": "Amount",
              "score": "Impact", "fraction": "Share of total"}
    _row(ws, ["Row type"] + [labels[c] for c in columns], header=True)
    for (activity, category), group in contributions.groupby(
            ["activity_label", "category_key"], sort=False, dropna=False):
        unit = group["method_unit"].iloc[0]
        reference = group["reference_unit"].iloc[0]
        row = _row(ws, [f"{activity} | {category} | Impact: {unit} | Reference: 1 {reference}"]
                   + [None] * len(columns), section=True)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(columns) + 1)
        ws.row_dimensions[row].height = 40
        for _, item in group.iterrows():
            root = pd.isna(item["parent"])
            row = _row(ws, ["Total (do not sum)" if root else "Input"] + [item[c] for c in columns])
            if root:
                for cell in ws[row]:
                    cell.font = Font(name=FONT, size=9, bold=True, color=TEXT)
            if "fraction" in columns:
                ws.cell(row, columns.index("fraction") + 2).number_format = "0.0%"
    _finish(ws, filter_rows=False)
    # Merged section headings span the whole report width.
    for merged in ws.merged_cells.ranges:
        ws.row_dimensions[merged.min_row].height = 32
    ws = _table(wb, "Contributions data", contributions)
    _table(wb, "Score checks", score_checks)
    notes = pd.DataFrame({"Notes": [
        "Table style adapted from Report example, AAK.dotx (TableGrid and green section rows).",
        "All results are for one reference-product unit. Impact units are in category labels or method_unit.",
        "Contribution totals and input rows must not be added together.",
        "Inputs include upstream impacts. Direct emissions and cutoff omissions can prevent inputs summing to the total.",
        "Contribution tables retain all branches passing CUTOFF; MAX_CONTRIBUTORS limits figures only.",
        "Amounts in the raw contribution data follow Brightway's recursive calculation output.",
        "This workbook exports the existing analysis tables; it does not contain a calculated life-cycle inventory.",
    ]})
    _table(wb, "Read me", notes)
    wb.save(path)
    return path
