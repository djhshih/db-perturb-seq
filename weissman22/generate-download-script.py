#!/usr/bin/env python3
import json
import requests


item_id = 20029387

# Set the base URL
BASE_URL = 'https://api.figshare.com/v2'

r = requests.get(BASE_URL + '/articles/' + str(item_id))

# Load the metadata as JSON
if r.status_code != 200:
    print('Something is wrong:',r.content)
else:
    metadata = json.loads(r.text)
    # # View metadata:
    # print(json.dumps(metadata, indent=2))
    
file_info = metadata["files"]

script_header="""#!/bin/bash
# Download dataset from Figshare

# Files cannot be downloaded via the download link obtained
# from the webpage
# We need to use the web API instead and provide the file ID
# The download link supplied by file information provided by the api call works as well

set -euo pipefail
IFS=$'\\n\\t'
"""

script = script_header

for i in range(len(file_info)):
    download_command = f"wget -O {file_info[i]["name"]} -c {file_info[i]["download_url"]}"
    script = f"{script}\n{download_command}"

script_name = "get.sh"

with open(script_name, "w") as f:
    f.write(script)

