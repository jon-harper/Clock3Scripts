#bom.py

import adsk.core, adsk.fusion
from ...lib import fusion360utils as futil
from ... import config

class MergeBomError(Exception):
    """
    Internally raised exception for ill-formed input.
    """
    def __init__(self, *args: object, part_id: str) -> None:
        super().__init__(*args)
        self.part_id = part_id

def extract_model_data(occurrences) -> list:
    """
    Iterates over an object, finding any parts with a PN prefix. For each occurrence, if the item is new, it creates a list entry. Otherwise, it increments the list count.

    occurrences: Any iterable object, typically a `list` or `OccurrenceList`.

    Returns: a `list` of `dict`s
    """
    ret = []
    for occ in occurrences:
        comp = occ.component
        if not comp.partNumber.startswith(config.PART_PREFIX):
            continue
        index = 0
        for item in ret:
            if item['component'] == comp:
                item['count'] += 1
                break
            index += 1

        if index == len(ret):
            ret.append({
                'component': comp,
                'name': comp.description,
                'count': 1,
                'ID': comp.partNumber
            })
    return ret

def pretty_format_bom(parts: dict) -> str:
     """
     Pseudo-pretty formats for display a `dict` of part data, typically as the result of an error.
     """
     ret = 'Part Number\tType\tCount\t\tUOMDescription\n'
     raw = "{}\t{}\t{}\t{}\n"
     for (id, item) in parts.items():
         if item['Value'] == 0:
             continue
         ret += raw.format(id, item['Type'], str(item['Value']), item['UOM'], item['Description'])
     return ret

def merge_source_data(bom: dict, 
                      parts : dict,
                      include_materials: bool = True,
                      include_supplies: bool = True):
    """
    Takes in part data from a model (`bom`) and source information (`parts`) and filters the data
    for empty entries. Flags modify if default values for materials and supplies are included.

    bom: A dict returned from the `extract_model_data()` function
    parts: A dict returned from `data_parser.import_source_data()`
    include_materials: A flag to include fabrication materials.
    include_supplies: A flag to include basic supplies for assembly and maintenance.
    """
    problems = []
    for line in bom:
        line_id = line['ID']
        if not line_id in parts.keys():
            problems.append(line_id)
            continue
        elif line['count'] == 0:
            continue
        elif line_id.startswith(config.PART_PREFIX) \
                or (include_materials and line_id.startswith(config.MATERIAL_PREFIX)) \
                or (include_supplies and line_id.startswith(config.SUPPLY_PREFIX)):
            try:
                parts[line_id]['Value'] = line['count']
            except Exception as e:
                futil.log(f'{line_id} failed: {line}')
                continue
    return (parts, problems)