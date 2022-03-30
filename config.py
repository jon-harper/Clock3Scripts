# Application Global Variables
# This module serves as a way to share variables across different
# modules (global variables).

import os

# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = True

# Gets the name of the add-in from the name of the folder the py file is in.
# This is used when defining unique internal names for various UI elements 
# that need a unique name. It's also recommended to use a company name as 
# part of the ID to better ensure the ID is unique.
ADDIN_PATH = os.path.dirname(__file__)
ADDIN_NAME = os.path.basename(ADDIN_PATH)
ADDIN_PREFIX = 'clk3'

PANEL_ID = 'Clock3Panel'
PANEL_NAME = 'Clock 3 Tools'
PANEL_DESCRIPTIOPN = 'Tools for the Clock 3 project.'
PANEL_BESIDE_ID = 'SolidScriptsAddinsPanel'

WORKSPACE_ID = 'FusionSolidEnvironment'

# Prefixes used for parsing part types
PART_PREFIX = 'PN'
MATERIAL_PREFIX = 'MN'
SUPPLY_PREFIX = 'UN'

def local_icon_folder(script_filename) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(script_filename)), 'resources')
    