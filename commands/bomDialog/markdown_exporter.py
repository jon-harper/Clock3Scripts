#markdown_exporter.py
from typing import Iterable, OrderedDict


BOM_STRINGS = { 
    "prefix" : \
"""
# Bill of Materials

The columns of this list are abbreviated for readability and reference. The
[Excel spreadsheet](https://github.com/jon-harper/clock-3/blob/main/BOM/bill_of_materials.xlsx)
version contains additional columns that are helpful in sourcing.

!!! warning
    The script that auto-generates this list cannot parse decimal values. Anything measured in length
    is measured in centimeters (cm) instead of meters (m) to work around this.
	
!!! note
    Materials are used in fabricating parts found later in the Bill of Materials or cable
    list. Some parts, particularly the acrylic and wood panels, will likely require outside
    fabrication.

!!! note
    All reference URLs and suppliers are purely for assistance in sourcing materials and are
    not endorsed.

!!! note
    The "Supplies" category includes a large number of components that are often already in the
    hands of experienced makers. As such, the list is primarily for reference and is not formally
    part of the Bill of Materials.

""",
    "section" : \
"""
## {title}

| ID | Description | UOM | Qty | Notes |
|:---|:------------|----:|----:|:------|
{table}

""",
    "suffix" : ""
}

class MarkdownExportError(Exception):
    pass

def format_sectioned_table(data : OrderedDict, section_key : str) -> str:
    LINE_FORMAT = '| {id} | {description} | {qty} | {uom} | {notes} |\n'
    LINE_FORMAT_URL = '| {id} | [{description}]({ref_url}) | {qty} | {uom} | {notes} |\n'

    #('Type', 'Description', 'UOM', 'Qty', 'RefSupplier', 'RefUrl', 'RefMfgr', 'RefMfgrPN', 'Notes')
    sections = OrderedDict()
    for row in data.values():
        if row[section_key] not in sections:
            sections[row[section_key]] = []

    keys = list(data.keys())
    keys.sort()
    for part_id in keys:
        part = data[part_id]
        if part['RefUrl'] is not None and part['RefUrl'] != '':
            formatted = LINE_FORMAT_URL.format(id=part_id, 
                                               description=part['Description'], 
                                               ref_url=part['RefUrl'], 
                                               qty=part['Qty'],
                                               uom=part['UOM'],
                                               notes=part['Notes'])
        else:
            formatted = LINE_FORMAT.format(id=part_id, 
                                           description=part['Description'], 
                                           qty=part['Qty'],
                                           uom=part['UOM'],
                                           notes=part['Notes'])
        sections[part[section_key]].append(formatted)
    result = ''
    for (title, section) in sections.items():
        table = ''
        for line in section:
            table += line
        result += BOM_STRINGS['section'].format(title=title, table=table)
    return result
            

def format_table(data : OrderedDict, include_id : bool = True) -> str:
    """
    Formats a part list for Markdown
    """
    NEW_LINE = '\n|'
    HEADERS = ('Description', 'UOM', 'Qty', 'RefUrl', 'Notes')
    HEADERS_ID = ('ID', 'Description', 'UOM', 'Qty', 'RefUrl', 'Notes')

    #Which format string we use is dependant on if the ID is included
    if (include_id):
        headers = HEADERS_ID
    else:
        headers = HEADERS

    result = '|'
    
    #Add the header line
    for key in headers:
        result += f' {key} |'
    result += NEW_LINE
    #Add the dashes
    for key in headers:
        result += '---|'

    #part_num is the 'ID' field, the rest we look up with the ID as key
    for part_num in data.keys():
        part : OrderedDict = data[part_num]
        result += NEW_LINE
        # only include the part number if requested
        if include_id:
            result += f' {part_num} |'
        for key in headers:
            result += f' {part[key]} |'
    result += '\n'
    return result
        
def export_markdown_bom(filepath : str, data: OrderedDict, section_key : str = '', include_id=True):
    try:
        #Adding a prefix? Just modify the constant
        out : str = BOM_STRINGS['prefix']
        
        #If requested, split into sections for simplified Markdown display
        if section_key != '':
            out += format_sectioned_table(data, section_key=section_key)
        else:
            out += format_table(data, include_id=True)
        
        #Adding a suffix? Just modify the constant.
        out += BOM_STRINGS['suffix']

        with open(filepath, 'w', newline='') as outfile:
            outfile.write(out)
    except Exception as e:
        raise MarkdownExportError('Export failed')