import os
import json

current_dir = os.path.dirname(os.path.realpath(__file__))
temp_src_dir = os.path.dirname(current_dir)
if temp_src_dir.__contains__('source'):
    root_dir = os.path.dirname(temp_src_dir)
else:
    root_dir = temp_src_dir

ROOT_DIR = root_dir
JSON_DIR = os.path.join(ROOT_DIR, 'settings.json')
MODEL_DIR = os.path.join(ROOT_DIR, 'best.pt')

with open(JSON_DIR, 'r') as settings_json:
    # load settings
    SETTINGS_DATA = json.load(settings_json)
