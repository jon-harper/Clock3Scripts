#Author: Jonathan Harper, 2022
#Description: Fusion 360 script. Extracts basic BOM data from active components containing "PN" in the part number field.
#
#Based on the fairly elementary ExportBOM script that ships with Fusion.

import adsk.core, adsk.fusion, traceback, os

from ...lib import fusion360utils as futil

from . import data_parser, bom, markdown_exporter
from ... import config

INITIAL_FILENAME = 'bom.csv'
CSV_FILTER = 'Comma Separated Values(*.csv);;All files(*.*)'
MARKDOWN_FILTER = 'Markdown Files(*.md);;All files(*.*)'
class Dialog:
    def __init__(self, command: adsk.core.Command, command_prefix: str, resource_path: str, local_handlers: list,) -> None:
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.command = command
        self.dialogId = f'{command_prefix}_dialog'
        self.resource_path = resource_path
        self.inputs = command.commandInputs
        self.local_handlers = local_handlers

    def warn(self, message: str, title: str = 'Warning') -> None:
        self.ui.messageBox(message, title)

    def inputFullName(self, shortname: str) -> str:
        return f'{self.dialogId}_{shortname}'

    def inputByShortName(self, shortname: str) -> adsk.core.CommandInput:
        return self.inputs.itemById(self.inputFullName(shortname))


# Command Inputs:
# Files Group Box       'fileGroup'         GroupCommandInput
#   Source File         'sourceBox'         BoolValueInput
#   Source Text         'sourceTextBox'     TextBoxCommandInput
#   Export Format       'exportFormatBox'   DropDownCommandInput
#   Export Dest         'exportDestBox'     BoolValueInput
#   Export Dest Text    'exportDestTextBox' TextBoxCommandInput
# Components Group Box  'componentGroup'    GroupCommandInput
#   Export Type         'exportTypeButton'  DropDownCommandInput
#   Component Selection 'selectionInput'    SelectionInput
# Options Group Box     'optionsGroup'      GroupCommandInput
#   Materials Button    'materialsButton'   BoolValueInput
#   Supplies Button     'suppliesButton'    BoolValueInput
class BomDialog(Dialog):
    """
    Controls the `CommandInput` objects and reacts to Command events.
    """

    def __init__(self, command: adsk.core.Command, command_prefix: str, resource_path: str, local_handlers) -> None:
        super().__init__(command, command_prefix, resource_path, local_handlers)
        futil.log(f'Bill of Materials Command Created Event')

        self.currentSource = os.path.normpath(os.path.join(config.ADDIN_PATH, 'source.csv'))
        self.currentDest = os.path.normpath(os.path.join(config.ADDIN_PATH, 'bill_of_materials.csv'))

        # File Group Box
        group = self.inputs.addGroupCommandInput(self.inputFullName('fileGroup'), 'Files')
        children = group.children
        
        sourceBox = children.addBoolValueInput(self.inputFullName('sourceBox'),
                                    'Source File', False, os.path.join(self.resource_path, 'import'))
        sourceBox.text = 'Set source file...'
        sourceBox.tooltip = 'Click to change the source file to process.'

        sourceTextBox = children.addTextBoxCommandInput(self.inputFullName('sourceTextBox'), 'Source File:', self.currentSource, 2, True)
        sourceTextBox.isFullWidth = True
        sourceTextBox.tooltip = 'This is the current source .csv file to process.'
        sourceTextBox.tooltipDescription = 'This file must be properly properly formatted. The latest version is in the Clock 3 git repository.'

        exportFormatBox = children.addDropDownCommandInput(self.inputFullName('exportFormatBox'),
                                    'Export Format', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        items = exportFormatBox.listItems
        items.add('Comma Separated Values', True)
        items.add('Markdown File', False)

        exportDestBox = children.addBoolValueInput(self.inputFullName('exportDestBox'),
                                    'Export File Location', False,  os.path.join(self.resource_path, 'export'))
        exportDestBox.text='Set destination file...'
        exportDestBox.tooltip='Click to change the output file and/or path for the bill of materials.'
        exportDestBox.tooltipDescription = 'The file must be a comma separated value (.csv) file.'

        exportDestTextBox = children.addTextBoxCommandInput(self.inputFullName('exportDestTextBox'), 'Export file:', self.currentDest, 2, True)
        exportDestTextBox.tooltip = 'The bill of materials will be output here.'
        exportDestTextBox.tooltipDescription = 'The file must be a comma separated value (.csv) file.'
        exportDestTextBox.isFullWidth = True
        
        # Component selection group box        
        group = self.inputs.addGroupCommandInput(self.inputFullName('componentGroup'), 'Components')
        children = group.children
        exportTypeButton = children.addDropDownCommandInput(
                                    self.inputFullName('exportType'),
                                    'Export components',
                                    adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        items = exportTypeButton.listItems
        items.add('Export all', True)
        items.add('Export active component', False)
        items.add('Select components to export', False)

        selectInput = children.addSelectionInput(self.inputFullName('selectionInput'), 'Export Selected', 'Select individual components to export')
        selectInput.addSelectionFilter(adsk.core.SelectionCommandInput.Occurrences)
        selectInput.setSelectionLimits(0)

        self.updateSelectedIndex()

        # Options group box
        group = self.inputs.addGroupCommandInput(self.inputFullName('optionsGroup'), 'Options')
        children = group.children

        button = children.addBoolValueInput(self.inputFullName('materialsButton'), 'Include materials', True, '', True)
        button.tooltip = 'Include raw materials that require assembly, such as insulation, wires, and connectors'
        button = children.addBoolValueInput(self.inputFullName('suppliesButton'), 'Include miscellaneous supplies', True, '', True)
        button.tooltip = 'Include assembly supplies such as wire strippers and lubricants'

        futil.add_handler(command.execute, self.executeEvent, local_handlers=local_handlers)
        futil.add_handler(command.inputChanged, self.inputEvent, local_handlers=local_handlers)
        futil.add_handler(command.validateInputs, self.validateInputs, local_handlers=local_handlers)
        futil.add_handler(command.select, self.selectionEvent, local_handlers=local_handlers)
        # futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)

        command.setDialogInitialSize(600, 600)

    def validateInputs(self, args: adsk.core.ValidateInputsEventArgs) -> None:
        """
        Checks that user input is valid and disables the 'OK' button if it is not.
        """
        if not os.path.exists(os.path.split(self.currentDest)[0]):
            args.areInputsValid = False
        elif not os.path.exists(self.currentSource):
            args.areInputsValid = False
        else:
            args.areInputsValid = True

    def selectionEvent(self, args : adsk.core.SelectionEventArgs):
        if args.selection.entity.objectType != adsk.fusion.Component.classType():
            return
        selectInput = adsk.core.SelectionCommandInput.cast(self.inputByShortName('selectionInput'))
        selectInput.addSelection(args.selection.entity)        

    def inputEvent(self, args: adsk.core.InputChangedEventArgs) -> None:
        """
        Handles indirect behavior from user input, e.g. enabling another input when a checkbox
        is toggled on.
        """
        if args.input == self.inputByShortName('sourceBox'):
            res = os.path.normpath(self.showFileDialog('Select source file', *os.path.split(self.currentSource), False, CSV_FILTER, 0, False))
            if len(res) and os.path.exists(res):
                box = adsk.core.TextBoxCommandInput.cast(self.inputByShortName('sourceTextBox'))
                assert(box)
                self.currentSource = res
                box.text = res
        elif args.input == self.inputByShortName('exportDestBox'):
            if self.formatBoxIndex() == 0:
                filter = CSV_FILTER
            else:
                filter = MARKDOWN_FILTER                
            res = os.path.normpath(self.showFileDialog('Select output file', *os.path.split(self.currentDest), True, filter, 0, False))
            if len(res) and os.path.exists(os.path.split(res)[0]):
                box = adsk.core.TextBoxCommandInput.cast(self.inputByShortName('exportDestTextBox'))
                assert(box)
                box.text = res
                self.currentDest = res
        elif args.input == self.inputByShortName('exportType'):
            self.updateSelectedIndex()
        elif args.input == self.inputByShortName('exportFormatBox'):
            formatBox = adsk.core.DropDownCommandInput.cast(args.input)
            old_path = self.currentDest
            if formatBox.selectedItem.index == 0 and old_path.endswith('.md'):
                new_path = old_path.removesuffix('.md') + '.csv'
            elif formatBox.selectedItem.index == 1 and old_path.endswith('.csv'):
                new_path = old_path.removesuffix('.csv') + '.md'
            else:
                self.warn('Could not auto-correct export file extension to new format.')
                return #bail
            destTextBox = adsk.core.TextBoxCommandInput.cast(self.inputByShortName('exportDestTextBox'))
            destTextBox.text = new_path
        else:
            pass
    def formatBoxIndex(self) -> int:
        formatBox = adsk.core.DropDownCommandInput.cast(self.inputByShortName('exportFormatBox'))
        return formatBox.selectedItem.index

    def executeEvent(self, event: adsk.core.CommandEventArgs) -> None:
        """
        Called when the OK/Export button is clicked.
        """
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            if not design:
                self.warn('No active design: Cannot extract bill of materials', 'Extract BOM')
                return

            occurences = self.getOccurrences(design)

            # Gather information about each unique component
            model_parts = bom.extract_model_data(occurences)
            source_data = data_parser.import_source_data(self.currentSource, True)
            try:
                # This does the grunt work for scraping the model
                (parts, problems) = bom.merge_source_data(
                        model_parts, 
                        source_data, 
                        self.getIncludeMaterials(), 
                        self.getIncludeSupplies())
                # Check for empty part IDs and clear
                empty_ids = []
                for (key, part) in parts.items():
                    if part['Qty'] == 0:
                        empty_ids.append(key)
                for key in empty_ids:
                    parts.pop(key)

            except bom.MergeBomException as e:
                self.warn(f'Cannot process part {e.part_id}; aborting')
                return

            if len(problems):
                self.warn(str(problems), 'Parts not found in source file')
            else:
                if self.formatBoxIndex() == 0:
                    data_parser.export_csv_bom(self.currentDest, parts)
                else:
                    markdown_exporter.export_markdown_bom(self.currentDest, parts, section_key='Type', include_id=False)
                self.ui.messageBox('Bill of Materials extracted.', 'Extract BOM')
            

        except:
            self.warn('Failed:\n{}'.format(traceback.format_exc()))

    def showFileDialog(self, 
                       title: str,
                       initial_filename: str,
                       initial_dir: str,
                       show_save: bool,
                       filter_str: str = 'All files(*.*)',
                       filter_index: int = 0,
                       multi_select: bool = False) -> str:
        """
        Gets the path of the file to save to.

        title: Dialog title
        initial_filename: Initial file to have selected/populating the line editor
        initial_dir: Path to start in
        show_save: Show a save dialog if `True`; show an open file dialog if `False`
        filter_str: A formatted string of file filters. See SDK documentation for format.
        filter_index: Start index in the filter list.
        multi_select: Allow multiple file selections. Not compatibile with `show_save` being `True`.

        Returns: a `str` with the full filepath.
        """
        
        fileDialog = self.ui.createFileDialog()
        fileDialog.title = title
        fileDialog.initialFilename = initial_filename
        fileDialog.initialDirectory = initial_dir
        fileDialog.filter = filter_str
        fileDialog.filterIndex = filter_index
        fileDialog.isMultiSelectEnabled = multi_select
        if show_save:
            res = fileDialog.showSave()
        else:
            res = fileDialog.showOpen()
        if res != adsk.core.DialogResults.DialogOK:
            return ''
        return fileDialog.filename

    def updateSelectedIndex(self) -> None:
        """
        Shows or hides the component selection command input based on the current export type.
        """
        box = adsk.core.DropDownCommandInput.cast(self.inputByShortName('exportType'))
        self.export_index = box.selectedItem.index
        selectInput = self.inputByShortName('selectionInput')
        if self.export_index == 2:
            selectInput.isVisible = True
        else:
            selectInput.isVisible = False
        futil.log(f'updateSelectedIndex: Index is {self.export_index}')

    def getOccurrences(self, design: adsk.fusion.Design):
        """
        Gets a list of occurrences to count for the BOM based on the current export type.
        """
        if self.export_index == 0: #export all
            return design.rootComponent.allOccurrences
        elif self.export_index == 1: #export active
            return design.activeComponent.allOccurrences
        else: #export selected
            return self.getSelectedComponents()

    def getIncludeMaterials(self) -> bool:
        """
        Returns `True` if the BOM will include raw materials.
        """
        button = adsk.core.BoolValueCommandInput.cast(self.inputByShortName('materialsButton'))
        return button.value

    def getIncludeSupplies(self) -> bool:
        """
        Returns `True` if the BOM will include miscellaneous supplies.
        """
        button = adsk.core.BoolValueCommandInput.cast(self.inputByShortName('suppliesButton'))
        return button.value

    def getSelectedComponents(self) -> list:
        """
        Returns the list of currently selected components. Note: this does not check parent/child relationships for parsing purposes.
        """
        selectInput = adsk.core.SelectionCommandInput.cast(self.inputByShortName('selectionInput'))
        ret = []
        if selectInput.selectionCount == 0:
            return ret
        for i in range(0, selectInput.selectionCount):
            entity = selectInput.selection(i).entity
            if entity.classType() == adsk.fusion.Occurrence.objectType:
                ret.append(adsk.fusion.Component.cast(entity))
        return ret