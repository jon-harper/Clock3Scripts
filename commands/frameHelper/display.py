#display.py

import adsk.core
import adsk.fusion
from ...lib import fusion360utils as futil

def get_occurrences() -> adsk.fusion.OccurrenceList:
    app = adsk.core.Application.get()
    ui = app.userInterface

    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        ui.messageBox('No active design', 'Extract BOM')    
        return
    return design.rootComponent.allOccurrences


def show_tee_nut_view() -> None:
    futil.log('show_tee_nut_view()_ called')
    items = get_occurrences()
    for item in items:
        comp = item.component
        pn: str = comp.partNumber
        if pn.startswith(('PN72', 'PN73', 'PN74', 'PN75', 'PN575')):
            item.isLightBulbOn = True
        elif pn.startswith('PN'):
            item.isLightBulbOn = False
        else:
            item.isLightBulbOn = True

def show_frame_view() -> None:
    futil.log('show_frame_view()_ called')
    items = get_occurrences()
    for item in items:
        comp = item.component
        pn: str = comp.partNumber
        if pn.startswith(('PN72', 'PN73', 'PN74', 'PN75', 'PN70', 'PN710')):
            item.isLightBulbOn = True
        elif pn.startswith('PN'):
            item.isLightBulbOn = False
        else:
            item.isLightBulbOn = True

def show_all():
    futil.log('show_all()_ called')
    for item in get_occurrences():
        item.isLightBulbOn = True