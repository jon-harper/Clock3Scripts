import adsk.core
import os
from ...lib import fusion360utils as futil

from .dialog import BomDialog

from ...import config

app = futil.app
ui = app.userInterface

CMD_ID = f'clk3_bomDialog'
CMD_NAME = 'Generate BOM'
CMD_Description = 'Bill of Materials generator for the Clock 3 project'

COMMAND_BESIDE_ID = ''
ICON_FOLDER = config.local_icon_folder(__file__)

local_handlers = []
dialog = None

def start():
    """
    Create the dialog command button.
    """
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    futil.add_handler(cmd_def.commandCreated, command_created)

    workspace = ui.workspaces.itemById(config.WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(config.PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    control.isPromoted = True

def stop():
    """
    Destroy the command on exit/unload.
    """
    workspace = ui.workspaces.itemById(config.WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(config.PANEL_ID)
    if panel:
        command_control = panel.controls.itemById(CMD_ID)
        if command_control:
            command_definition = ui.commandDefinitions.itemById(CMD_ID)
            command_control.deleteMe()
            if command_definition:
                command_definition.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    global dialog, local_handlers
    dialog = BomDialog(args.command, ICON_FOLDER, local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

def command_destroy(args: adsk.core.CommandEventArgs):
    """
    Called when the command ends; clears event handler references.
    """
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers, dialog
    dialog = None
    local_handlers = []
