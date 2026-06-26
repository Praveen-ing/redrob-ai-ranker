import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
JD_RULES_PATH = os.path.join(DATA_DIR, 'jd_rules.json')

WEIGHTS = {
    'skills': 40,
    'experience': 30,
    'behavioral': 20,
    'location': 10
}

with open(JD_RULES_PATH, 'r') as f:
    JD_RULES = json.load(f)
