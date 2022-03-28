#Author: Jonathan Harper, 2022
#Description: Fusion 360 script. Extracts basic BOM data from active components containing "PN" in the part number field.
#Original Author: Autodesk Inc.

import adsk.core, adsk.fusion, traceback
from ...lib import fusion360utils as futil

from . import data_parser
from . import bom

class Dialog:
    def __init__(self, command: adsk.core.Command) -> None:
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.command = command

    def warn(self, message: str, title: str = 'Extract BOM') -> None:
        self.ui.messageBox(message, title)

class BomDialog(Dialog):
    def __init__(self, command: adsk.core.Command, local_handlers) -> None:
        super().__init__(command)
        self.local_handlers = local_handlers
        futil.log(f'Bill of Materials Command Created Event')

        # Get a reference to the command inputs
        inputs = command.commandInputs

        # TODO Define the dialog for your command by adding different inputs to the command.

        futil.add_handler(command.execute, self.executeEvent, local_handlers=local_handlers)
        futil.add_handler(command.inputChanged, self.inputEvent, local_handlers=local_handlers)
        futil.add_handler(command.validateInputs, self.validateInputs, local_handlers=local_handlers)
        # futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)

    def validateInputs(self, args: adsk.core.ValidateInputsEventArgs) -> None:
        """
        Checks that user input is valid and disables the 'OK' button if it is not.
        """

    def inputEvent(self, event: adsk.core.InputChangedEventArgs) -> None:
        """
        Handles indirect behavior from user input, e.g. enabling another input when a checkbox
        is toggled on.
        """
        pass

    def executeEvent(self, event: adsk.core.CommandEventArgs) -> None:
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            if not design:
                self.warn('No active design', 'Extract BOM')
                return

            # Get all occurrences in the root component of the active design
            # occurences = get_occurences(design)
            occurences = self.getOccurences(design)

            # Gather information about each unique component
            model_parts = bom.generate_bom(occurences)
            
            source_data = data_parser.import_source_data(self.sourcePath())
            (parts, problems) = bom.merge_source_data(model_parts, source_data)
            if problems.count:
                self.warn(str(problems), 'Parts not found in source file')
            else:
                data_parser.export_data(self.destinationPath(), parts)
                self.ui.messageBox('Bill of Materials extracted.', 'Extract BOM')

        except:
            self.warn('Failed:\n{}'.format(traceback.format_exc()))

    def sourcePath(self) -> str:
        return 'C:/Users/jon/Documents/3D Print/Clockmaker/clock-3/BOM/source.csv'

    def destinationPath(self) -> str:
        return 'C:/Users/jon/Documents/3D Print/Clockmaker/out.csv'

    def getOccurences(self, design: adsk.fusion.Design) -> adsk.fusion.OccurrenceList:
        return design.rootComponent.allOccurrences
