import json
import requests
from pathlib import Path

item_ids = [20029387]

# Set the base URL
BASE_URL = 'https://api.figshare.com/v2'

file_info = []

for i in item_ids:
    r = requests.get(BASE_URL + '/articles/' + str(i) + '/files')
    file_metadata = json.loads(r.text)
    for j in file_metadata: #add the item id to each file record- this is used later to name a folder to save the file to
        j['item_id'] = i
        file_info.append(j) #Add the file metadata to the list

print(file_info)

