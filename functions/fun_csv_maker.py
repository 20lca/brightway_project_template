"""Convert fixed-layout Excel LCA matrices to legacy SimaPro 7 CSV.

Python 3.10+, standard library only. Reads saved Excel values, never calculates.
Based on 2.-0 LCA Consultants' CSVmaker-crossplatform4 VBA macro.
"""
from __future__ import annotations
import argparse
import math
import posixpath
import re
import warnings
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SECTIONS = [('', 'Materials/fuels'), ('Raw', 'Resources'), ('Air', 'Emissions to air'),
            ('Water', 'Emissions to water'), ('Soil', 'Emissions to soil'),
            ('Waste', 'Final waste flows'), ('Non mat.', 'Non material emission'),
            ('Social', 'Social issues'), ('Economic', 'Economic issues'),
            ('Wastetotreatment', 'Waste to treatment')]
META = ['Time Period', 'Geography', 'Technology', 'Representativeness',
        'Multiple output allocation', 'Substitution allocation', 'Cut off rules',
        'Capital goods', 'Boundary with nature']
HEADER = ['{CSV separator: Semicolon}', '{CSV Format version: 7.0.0}',
          '{Decimal separator: .}', '{Date separator: /}',
          '{Short date format: dd/MM/yyyy}', '']

class ConversionError(ValueError):
    """Invalid layout, missing calculation, or invalid exchange data."""

def _col(text):
    n = 0
    for x in text: n = 26*n + ord(x)-64
    return n

class _Workbook:
    """Sparse OOXML reader: ignores inflated worksheet dimensions and formatting."""
    def __init__(self, path):
        self.path = Path(path)
        if self.path.suffix.lower() not in ('.xlsx', '.xlsm'):
            raise ConversionError(f'{path}: save as .xlsx or .xlsm in Excel first.')
        self.zip = zipfile.ZipFile(path)
        self.shared = []
        if 'xl/sharedStrings.xml' in self.zip.namelist():
            root = ET.fromstring(self.zip.read('xl/sharedStrings.xml'))
            self.shared = [''.join(t.text or '' for t in s.findall('.//m:t', NS)) for s in root]
        rels = ET.fromstring(self.zip.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels}
        root = ET.fromstring(self.zip.read('xl/workbook.xml'))
        self.sheets = {}
        for s in root.find('m:sheets', NS):
            target = targets[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            self.sheets[s.get('name')] = (target.lstrip('/') if target.startswith('/')
                else posixpath.normpath('xl/' + target))

    def read(self, name):
        if name not in self.sheets:
            raise ConversionError(f'{self.path.name}: sheet {name!r} not found.')
        cells, errors = {}, {}
        root = ET.fromstring(self.zip.read(self.sheets[name]))
        for c in root.findall('.//m:sheetData/m:row/m:c', NS):
            ref = c.get('r'); letters, row = re.fullmatch(r'([A-Z]+)(\d+)', ref).groups()
            key = (int(row), _col(letters)); typ = c.get('t'); v = c.find('m:v', NS)
            raw = v.text if v is not None else None
            if c.find('m:f', NS) is not None and (v is None or (raw is None and typ != 'str')):
                errors[key] = f'{name}!{ref}: missing saved formula result; recalculate and save in Excel.'
            if typ == 'e': errors[key] = f'{name}!{ref}: Excel error {raw}.'
            if typ == 's': value = self.shared[int(raw)]
            elif typ == 'inlineStr': value = ''.join(t.text or '' for t in c.findall('.//m:t', NS))
            elif typ in ('str', 'e'): value = raw or ''
            elif typ == 'b': value = bool(int(raw or 0))
            elif raw is not None: value = float(raw)
            else: value = None
            if value not in (None, ''): cells[key] = value
        return _Sheet(name, cells, errors)

class _Sheet:
    def __init__(self, name, cells, errors=None):
        self.name, self.cells, self.errors = name, cells, errors or {}
    def get(self, row, col):
        if (row, col) in self.errors: raise ConversionError(self.errors[row, col])
        return self.cells.get((row, col), '')

def _text(value):
    if isinstance(value, bool): raise ConversionError('Boolean value in export data.')
    if isinstance(value, (float, int)):
        if not math.isfinite(value): raise ConversionError('Non-finite number in export data.')
        return format(value, '.15g')
    s = str(value)
    if any(ch in s for ch in '\r\n'):
        raise ConversionError(f'Unsupported newline in field: {s!r}')
    return s

def _field(value, force_quote=False):
    """Quote semicolon-separated fields and escape embedded double quotes."""
    text = _text(value)
    if force_quote or ';' in text or '"' in text:
        return '"' + text.replace('"', '""') + '"'
    return text

def _layout(s, start):
    base = start-4
    for row, col, expected in [(1,start-1,'Product'), (2,start-1,'Unit'),
            (5,start-1,'Category'), (6,start-1,'Comment'), (7,base,'Compartment'),
            (7,base+1,'Product/Substance'), (7,base+2,'Sub-compartment'), (7,start-1,'Type')]:
        if s.get(row,col) != expected:
            raise ConversionError(f'{s.name}: expected {expected!r} at row {row}, column {col}. '
                                  'Use first_process_column="F" for DEA or "E" for the legacy template.')
    # Match VBA's Do While Cells(1, Col).Value <> "": stop at the
    # first empty header, even when archived processes exist farther right.
    cols = []
    col = start
    while s.get(1, col) != '':
        cols.append(col)
        col += 1
    if not cols:
        raise ConversionError(f'{s.name}: no process name in row 1, column {start}.')
    names = [str(s.get(1,c)).strip() for c in cols]
    if len(set(names)) != len(names): raise ConversionError(f'{s.name}: duplicate process names.')
    return cols

def _render(s, start, uncertainties, ustart, include_subcompartments):
    cols = _layout(s,start); base = start-4
    rows = sorted({r for r,c in set(s.cells)|set(s.errors) if r>=8 and base<=c<=cols[-1]})
    groups = {key: [] for key,_ in SECTIONS}; rank = 0
    for row in rows:
        name = s.get(row,base+1)
        active = any(s.get(row,c) != '' for c in cols)
        if name == '':
            if active: raise ConversionError(f'{s.name}: exchange values without a name in row {row}.')
            continue
        comp = s.get(row,base)
        if comp not in groups: raise ConversionError(f'{s.name}: unknown compartment {comp!r}, row {row}.')
        order = list(groups).index(comp)
        if order < rank: raise ConversionError(f'{s.name}: compartment order invalid at row {row}.')
        rank = order; groups[comp].append(row)
        if s.get(row,base+2) != '' and not include_subcompartments:
            warnings.warn(f'{s.name}, row {row}: sub-compartment omitted to match supplied VBA. '
                          'Use include_subcompartments=True to export it.', stacklevel=2)
    out = list(HEADER)
    for col in cols:
        pname = _text(s.get(1,col)); unit = _field(s.get(2,col)); amount = s.get(3,col)
        category = _field(s.get(5,col)); ctype = _field(s.get(7,col))
        if not unit or amount == '' or not ctype:
            raise ConversionError(f'{s.name}: missing unit, reference amount or type for {pname}.')
        u = None
        if uncertainties is not None:
            u = uncertainties.get(pname.strip())
            if u is None: raise ConversionError(f'Uncertainty process not found: {pname!r}.')
        out += ['Process','','Category type',ctype,'']
        for field in META: out += [field,'Unspecified','']
        out += ['','Record','','','Generator','','','Literature references','','',
                'Collection method','','','Data treatment','','','Verification','Comment','',
                'Comment',_field(s.get(6,col)),'','System description;','','Products',
                f'{_field(pname, True)}; {unit}; {_field(amount)}; 100%; not defined; {category};','']
        for comp, title in SECTIONS:
            out.append(title)
            for row in groups[comp]:
                val = s.get(row,col)
                if val == '': continue  # Explicit numeric zero is preserved.
                name = _text(s.get(row,base+1)); eu = _field(s.get(row,start-1))
                if not eu: raise ConversionError(f'{s.name}: missing unit at row {row}.')
                tail = ';Undefined; 0;0;0;'
                if u:
                    us, uc = u
                    for offset in range(4):
                        if us.get(row,ustart-4+offset) != s.get(row,base+offset):
                            raise ConversionError(f'Uncertainty row mismatch: {pname}, row {row}.')
                    factor = us.get(row,uc)
                    if isinstance(factor,bool) or not isinstance(factor,(int,float)) or not math.isfinite(factor) or factor<1:
                        raise ConversionError(f'{pname}, row {row}: uncertainty factor must be numeric and >= 1.')
                    tail = f';Lognormal;{_text(factor)};0;0;'
                if comp == '': line = f'{_field(name, True)};{eu};{_field(val)}'
                elif comp == 'Wastetotreatment': line = f'{_field(name)};{eu};{_field(val)}'
                else:
                    sub = _field(s.get(row,base+2)) if include_subcompartments else ''
                    line = f'{_field(name)};{sub};{eu};{_field(val)}'
                out.append(line+tail)
            out.append('')
        out += ['End','']
    return '\r\n'.join(out)+'\r\n'

def csv_maker(excel_file, sheets, output_dir='output', *, first_process_column='F',
              uncertainty_file=None, uncertainty_sheets=None, uncertainty_first_process_column=None,
              include_subcompartments=False, encoding='cp1252', overwrite=False):
    """Return one output Path per sheet. Fixed header rows 1-7; exchanges from row 8.

    Default layout: B compartment, C name, D sub-compartment, E unit, F+ processes.
    Use first_process_column='E' for A:D metadata and E+ processes.
    Export stops at the first empty row-1 header; all columns beyond it are ignored.
    The same rule applies to selected uncertainty worksheets.
    Uncertainty sheets must have the same row numbers/labels/units; process columns
    may be reordered. Factors are passed through as SimaPro lognormal uncertainty
    factors (NOT converted to Brightway sigma). .xls must first be saved as .xlsx.
    All selected sheets validate before any output is written. Existing files are
    refused unless overwrite=True. Excel cache freshness cannot be established.
    """
    if first_process_column not in ('E','F'): raise ConversionError('Choose fixed layout E or F.')
    start = _col(first_process_column)
    ustart = _col(uncertainty_first_process_column or first_process_column)
    if ustart not in (5,6): raise ConversionError('Choose uncertainty layout E or F.')
    sheets = [sheets] if isinstance(sheets,str) else list(sheets)
    if not sheets or len(set(sheets)) != len(sheets): raise ConversionError('Supply unique sheet names.')
    if uncertainty_sheets is not None and uncertainty_file is None:
        raise ConversionError('uncertainty_sheets requires uncertainty_file.')
    wb = _Workbook(excel_file); uw = None
    try:
        index = None
        if uncertainty_file is not None:
            uw = _Workbook(uncertainty_file); index = {}
            selected = uncertainty_sheets or list(uw.sheets)
            if isinstance(selected,str): selected = [selected]
            for name in selected:
                us = uw.read(name)
                for col in _layout(us,ustart):
                    pname = str(us.get(1,col)).strip()
                    if pname in index: raise ConversionError(f'Duplicate uncertainty process: {pname}.')
                    index[pname] = (us,col)
        planned = []
        for name in sheets:
            safe = re.sub(r'[^\w.-]+','_',name).strip('._') or 'sheet'
            path = Path(output_dir)/f'{Path(excel_file).stem}_{safe}.CSV'
            data = _render(wb.read(name),start,index,ustart,include_subcompartments).encode(encoding)
            if path.exists() and not overwrite: raise FileExistsError(path)
            if any(str(p).casefold()==str(path).casefold() for p,_ in planned):
                raise ConversionError('Sheet names produce colliding output filenames.')
            if path.resolve() in {Path(excel_file).resolve(), Path(uncertainty_file).resolve() if uncertainty_file else None}:
                raise ConversionError('Output would overwrite an input.')
            planned.append((path,data))
        Path(output_dir).mkdir(parents=True,exist_ok=True)
        for path,data in planned:
            with path.open('wb' if overwrite else 'xb') as stream: stream.write(data)
        return [path for path,_ in planned]
    finally:
        wb.zip.close()
        if uw: uw.zip.close()

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('excel_file'); p.add_argument('--sheets',nargs='+',required=True)
    p.add_argument('--output-dir',default='output'); p.add_argument('--first-process-column',choices=['E','F'],default='F')
    p.add_argument('--uncertainty-file'); p.add_argument('--uncertainty-sheets',nargs='+')
    p.add_argument('--uncertainty-first-process-column',choices=['E','F'])
    p.add_argument('--include-subcompartments',action='store_true'); p.add_argument('--overwrite',action='store_true')
    p.add_argument('--encoding',default='cp1252')
    for result in csv_maker(**vars(p.parse_args())): print(result)
