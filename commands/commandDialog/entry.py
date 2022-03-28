import adsk.core
import os
from ...lib import fusion360utils as futil

app = adsk.core.Application.get()
ui = app.userInterface

# TODO: Specify the basic command information
CMD_ID = f'clk3_cmdDialog'
CMD_NAME = 'Command Dialog Sample'
CMD_Description = 'A Fusion 360 Add-in Command with a dialog'

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'

#TODO: Specify which command this is next to
COMMAND_BESIDE_ID = 'cl3_bomDialog'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used prevent garbage collection.
local_handlers = []

def start():
    """
    Creates the dialog command button.
    """

    # Create a new command definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Add an event handler to be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # Add the command to the UI.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command can be promoted to the main toolbar. 
    control.isPromoted = False


def stop():
    """
    Destroy the command on exit/unload.
    """
    # Get the UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control and parent definition
    if command_control:
        command_control.deleteMe()
    if command_definition:
        command_definition.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    """
    Define the contents of the dialog when invoked.
    """
    futil.log(f'{CMD_NAME} Command Created Event')

    # Get a reference to the command inputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    
    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    # futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    # futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    """
    Handle the user clicking 'OK' if command inputs were added to the dialog. Otherwise,
    called immediately after the `CommandCreatedEvent`.
    """
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs


def command_preview(args: adsk.core.CommandEventArgs):
    """
    Called when the command needs to compute a new preview in the graphics window.
    """
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    """
    Called when the user interacts with the dialog *after* the dialog has registered the
    input but before it is shown. This lets allows other inputs to adjust based on the
    changed value or button click, et cetera.
    """
    changed_input = args.input
    inputs = args.inputs

    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    """
    Checks that user input is valid and disables the 'OK' button if it is not.
    """
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values.
    # This controls if the OK button is enabled or not.
    #
    # valueInput = inputs.itemById('value_input')
    # if valueInput.value >= 0:
    #     inputs.areInputsValid = True
    # else:
    #     inputs.areInputsValid = False
        

def command_destroy(args: adsk.core.CommandEventArgs):
    """
    Called when the command ends; clears event handler references.
    """
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
