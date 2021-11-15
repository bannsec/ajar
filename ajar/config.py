import appdirs
import os
import json
from sys import exit

def init():
    """
    Initialize the configuration.
    """
    global config

    # Config is a dictionary
    # Keys:
    #   - 'stockfish_path'

    # Attempt to load the config file using CONFIG_FULLPATH as json file
    try:
        with open(CONFIG_FULLPATH, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # If the config file does not exist, create it
        config = {'stockfish_path': None}
        save()

    # Check if all the prerequisites are met
    prechecks()

def save():
    """
    Save the config file.
    """
    with open(CONFIG_FULLPATH, 'w') as f:
        json.dump(config, f, indent=4)

def prechecks():
    """
    Check if all the prerequisites are met.
    """

    # Check if stockfish path is set
    if config['stockfish_path'] is None:
        # If not, prompt user to set it
        print("An engine (such as stockfish) is required for ajar. You can download it for free here: https://stockfishchess.org/download/")
        config['stockfish_path'] = input('Please enter the path to your stockfish executable: ')
        save()

    # Check if stockfish path is valid and executable
    if not os.path.isfile(config['stockfish_path']):
        print('The path to your stockfish executable is invalid.')
        # unset the stockfish path
        config['stockfish_path'] = None
        save()
        exit(1)
    if not os.access(config['stockfish_path'], os.X_OK):
        print('The path to your stockfish executable is not executable.')
        # unset the stockfish path
        config['stockfish_path'] = None
        save()
        exit(1)

# Create appdirs object
app_dirs = appdirs.AppDirs('ajar', 'bannsec')
os.makedirs(app_dirs.user_data_dir, exist_ok=True)

CONFIG_FILENAME = 'config.json'
CONFIG_FULLPATH = os.path.join(app_dirs.user_data_dir, CONFIG_FILENAME)

try:
    config
except NameError:
    init()