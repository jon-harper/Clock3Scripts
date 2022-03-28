from .bomDialog import entry as bomDialog
from .frameHelper import entry as frameHelper

# List of all commands
commands = [
    bomDialog,
    frameHelper
]

# Iterate over entry.py in each command's folder and call `start()`
def start():
    for command in commands:
        command.start()

# Iterate over entry.py in each command's folder and call `stop()`
def stop():
    for command in commands:
        command.stop()