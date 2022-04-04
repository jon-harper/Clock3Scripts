#markdown_exporter.py
from typing import Iterable, OrderedDict


BOM_STRINGS = { 
    "prefix" : \
"""
# Bill of Materials

The columns of this list are abbreviated for readability and reference. The
[Excel spreadsheet](https://github.com/jon-harper/clock-3/blob/main/BOM/bill_of_materials.xlsx)
version contains columns that are helpful in actual sourcing.

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

def split_by_section(data: OrderedDict, section_key: str, headers : Iterable) -> OrderedDict:
    #Grab what sections are in the data
    sections = []
    for row in data.values():
        if row[section_key] not in sections:
            sections.append(row[section_key])
    
    #result: OrderedDict[str, OrderedDict[str, str]]
    result = OrderedDict.fromkeys(sections, OrderedDict.fromkeys(headers, ''))
    
    #Determine which columns to include. 'ID' is a dict key, so we flag it separately.
    columns = list(headers)
    if 'ID' in columns:
        columns.remove('ID')

    #Iterate over each part
    for part_id in data.keys():
        #Capture both the ID and data
        part : OrderedDict = data[part_id]
        
        #Get the section from the data dict
        section : str = part[section_key]
        section_dict : OrderedDict = result[section]
        
        #Iterate over the OrderedDict and copy values, but only with the headers we want
        item = OrderedDict.fromkeys(headers, '')
        for column in columns:
            item[column] = part[column]
        section_dict[part_id] = item
    return result

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