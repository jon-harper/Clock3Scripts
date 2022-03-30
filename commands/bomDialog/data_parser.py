import csv
from typing import OrderedDict

####
# CSV Columns/Headers
####
# Import header (ID as dict key):
# ('ID', 'Type', 'Description', 'UOM', 'DefaultValue', 'RefSupplier', 'RefUrl', 'RefMfgr', 'RefMfgrPN', 'Notes')
# 
####
# Export header:
# ('ID', 'Type', 'Description', 'UOM', 'Value', 'RefSupplier', 'RefUrl', 'RefMfgr', 'RefMfgrPN', 'Notes')
#

class ImportError(Exception):
    pass

class ExportError(Exception):
    pass

def parse_row_data(row: OrderedDict[str, str], include_value = False) -> dict:
    """
    Called by `import_source_data()` to parse through a row of CSV data.
    """
    result = {
            'Type': row['Type'],
            'Description': row['Description'],
            'UOM': row['UOM'],
            'Value' : 0, #we read in the default value later
            'RefSupplier': row['RefSupplier'],
            'RefUrl': row['RefUrl'],
            'RefMfgr': row['RefMfgr'],
            'RefMfgrPN': row['RefMfgrPN'],
            'Notes': row['Notes'] 
        }
    if include_value and row['DefaultValue'] is not None and row['DefaultValue'].isnumeric():
        result['Value'] = int(row['DefaultValue'])
    return result

def import_source_data(filepath: str = None,
                       include_defaults: bool = True) -> dict:
    """
    Imports values from a source file for a bill of materials. This does not perform any error checking.

    filepath: A string with the full file path and name.
    include_defaults: If `True`, includes default values hard-coded into the .csv. This is useful for the master BOM.
    include_materials: If `True`, include materials that need fabrication. This is useful for the master BOM.
    include_supplies: If `True`, include miscellaneous supplies for assembling and maintaining the printer.

    Returns a dict of dicts with string keys. The part number is the key, e.g. 'PN001' is a key.
    """
    result = {}
    try:
        with open(filepath, 'r', newline='') as datafile:
            fieldnames=('ID', 'Type', 'Description', 'UOM', 'DefaultValue', 'RefSupplier', 'RefUrl', 'RefMfgr', 'RefMfgrPN', 'Notes')
            reader = csv.DictReader(datafile, fieldnames=fieldnames, dialect='excel')
            for row in reader:
                result[row['ID']] = parse_row_data(row, include_defaults)
    except Exception as e:
        raise ImportError('Failed to process source file') from e
    return result

def export_data(filepath: str, data: dict) -> None:
    """
    Exports data for a bill of materials.

    filepath: A string with the full file path and name.
    data: A dict containing the data to export.
    """
    try:
        with open(filepath, 'w', newline='') as datafile:
            fieldnames=('ID', 'Type', 'Description', 'UOM', 'Value', 'RefSupplier', 'RefUrl', 'RefMfgr', 'RefMfgrPN', 'Notes')
            writer = csv.DictWriter(datafile, fieldnames, dialect=csv.excel)
            writer.writeheader()
            for part_num in data.keys():
                if data[part_num]['Value'] == 0:
                    continue
                outdata = data[part_num]
                outdata['ID'] = part_num
                writer.writerow(outdata)
                
    except Exception as e:
        raise ExportError('Failed to export data') from e