#!/usr/bin/env python3
import json
import requests


item_ids = [28589774]

# Set the base URL
BASE_URL = 'https://api.figshare.com/v2'

file_info = []

for i in item_ids:
    r = requests.get(BASE_URL + '/articles/' + str(i) + '/files')
    file_metadata = json.loads(r.text)
    for j in file_metadata: #add the item id to each file record- this is used later to name a folder to save the file to
        j['item_id'] = i
        file_info.append(j) #Add the file metadata to the list


script_header="""#!/bin/bash
# Download dataset from Figshare

# Files cannot be downloaded via the download link obtained from the webpage
# We need to use the web API instead and provide the file ID
# The download link supplied by the api call to retrieve file info works as well

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

