import json
import sys
import os

# Add the parent directory to Python path to find modules properly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Now we can import modules from both the parent directory and this directory
from service.elevenlabs_api import load_tools_into_agent

# Get the full path to some.json (it's in the same directory as this script)
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "some.json")
data = json.load(open(json_path))

load_tools_into_agent("uk6PZ0r2DczJXvs5SXO9")
