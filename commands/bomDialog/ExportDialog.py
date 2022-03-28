import adsk.core, traceback

def getInitialDirectory() -> str:
    """
    Returns the stored initial directory for the filename dialog (if it is availabe).
    """
    return ''

#        out_file = getFilename()
#        if out_file == '':
#            _state.ui.messageBox('Operation Cancelled', 
#                          'BOM Generator',
#                          adsk.core.MessageBoxButtonTypes.OKButtonType,
#                          adsk.core.MessageBoxIconTypes.WarningIconType)
#            return

def getFilename() -> str:
    """
    Gets the path of the file to save to.
    """
    global _state
    fileDialog = _state.ui.createFileDialog()
    fileDialog.title = 'Choose output file'
    fileDialog.initialFilename = 'bom.tsv'
    fileDialog.initialDirectory = getInitialDirectory()
    fileDialog.filter = ('Tab Separated Values (*.tsv;*.tab);;All files(*.*')
    fileDialog.filterIndex = 0
    fileDialog.isMultiSelectEnabled = False
    
    res = fileDialog.showSave()
    if res != adsk.core.DialogResults.DialogOK:
        return ''
    return fileDialog.filename()

class DestroyHandler(adsk.core.CommandEventHandler):
    """
    Cleanup handler for the command dialog
    """
    def __init__(self):
        super().__init__()

    def notify(self, eventArgs: adsk.core.CommandEventArgs) -> None:
        global _script
        try:
            adsk.terminate()
        except:
            _script.showError('Failed:\n{}'.format(traceback.format_exc()), 
                            'CommandDestroyHandler.notify()')

class InputHandler(adsk.core.InputChangedEventHandler):
    """
    Handles input events
    """
    def __init__(self):
        super().__init__()

    def notify(self, eventArgs: adsk.core.InputChangedEventArgs) -> None:
        global _script
        try:
            eventInput = eventArgs.input
            if eventInput.id == 'clk3_sourceFile':
                pass
            elif eventInput.id == 'clk3_destFile':
                pass

            elif eventInput.id == 'clk3_doExport':
                _script.ui.messageBox('Export BOM')
            else:
                super().notify(eventArgs)
        except:
            _script.showError('Failed:\n{}'.format(traceback.format_exc()), 
                            'InputHandler.notify()')

class ExecuteHandler(adsk.core.CommandEventHandler):
    """
    Executes the export.
    """
    def __init__(self):
        super().__init__()

    def notify(self, eventArgs: adsk.core.CommandEventArgs) -> None:
        global _script
        try:
            _script.ui.messageBox('Reached Execute Handler!')
            super().notify(eventArgs)
        except:
            _script.showError('Failed:\n{}'.format(traceback.format_exc()), 
                              'CommandExecuteHandler.notify()')