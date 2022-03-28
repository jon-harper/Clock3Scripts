#Author- Jonathan Harper
#Description- Testing ground for UI Stuff.

from distutils.util import execute
import adsk.core
import adsk.fusion
import traceback

from .Script import FusionScript
from .ExportDialog import InputHandler, DestroyHandler, ExecuteHandler

_script = FusionScript()

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """
    After a command is created, this handler's `notify()` method creates the dialog and hooks up event
    handlers.
    """
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs) -> None:
        global _script
        try:
            cmd = args.command
            # cmd.okButtonText = 'Export'
            cmd.isOKButtonVisible = False
            
            # Connect event handlers
            destroyHandler = DestroyHandler()
            cmd.destroy.add(destroyHandler)
            _script.handlers.append(destroyHandler)

            inputHandler = InputHandler()
            cmd.inputChanged.add(inputHandler)
            _script.handlers.append(inputHandler)

            executeHandler = ExecuteHandler()
            cmd.execute.add(executeHandler)
            _script.handlers.append(executeHandler)

            inputs = cmd.commandInputs

            group = inputs.addGroupCommandInput('clk3_fileGroup', 'Files')
            children = group.children
            sourceBox = children.addBoolValueInput('clk3_sourceData',
                                     'Source File', False, 'resources/import')
            sourceBox.text = 'Set source file...'
            exportBox = children.addBoolValueInput('clk3_exportFile',
                                     'Export File Location', False, 'resources/export')
            exportBox.text='Filename'
            
            group = inputs.addGroupCommandInput('clk3_componentGroup', 'Components')
            children = group.children
            exportTypeButton = children.addDropDownCommandInput(
                                        'clk3_exportAll',
                                        'Export components',
                                        adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            items = exportTypeButton.listItems
            items.add('Export all', True)
            items.add('Export active component', False)
            items.add('Export only selected', False)
            #select components box here

            processButtom = inputs.addBoolValueInput('clk3_doExport', 'Export BOM', False, '')
            processButtom.isFullWidth = True
            processButtom.text = 'Export BOM'


        except:
            _script.showError('Failed:\n{}'.format(traceback.format_exc()), 'CommandCreatedHandler.notify()')

def run(context) -> None:
    global _script
    try:
        _script.startup()

        #try and retrieve the command if it already exists.
        cmdDef = _script.ui.commandDefinitions.itemById('uiTest')
        if not cmdDef:
            cmdDef = _script.ui.commandDefinitions.addButtonDefinition('uiTest', 'BOM Export Tool', 'Tooltip here.')

        commandHandler = CommandCreatedHandler()
        cmdDef.commandCreated.add(commandHandler)
        _script.handlers.append(commandHandler)

        cmdDef.execute()

        adsk.autoTerminate(False)

    except:
        if _script.ui:
            _script.showError('Failed:\n{}'.format(traceback.format_exc()), 'Error')