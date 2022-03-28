from . import commands
from .lib import fusion360utils as futil

from . import config

def run(context):
    try:
        ui = futil.app.userInterface
        workspace = ui.workspaces.itemById(config.WORKSPACE_ID)
        workspace.toolbarPanels.add(config.PANEL_ID, config.PANEL_NAME,
                                            config.PANEL_BESIDE_ID, False)
        commands.start()
    except:
        futil.handle_error('run')


def stop(context):
    try:
        futil.clear_handlers()
        commands.stop()

        ui = futil.app.userInterface
        workspace = ui.workspaces.itemById(config.WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(config.PANEL_ID)
        panel.deleteMe()
    except:
        futil.handle_error('stop')