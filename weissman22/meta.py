
import datetime
import json
import requests

# Set the base URL and ITEM_ID
BASE_URL = 'https://api.figshare.com/v2'

ITEM_ID = 20029387

#Retrieve public metadata from the endpoint
r = requests.get(BASE_URL + '/articles/' + str(ITEM_ID))

# Load the metadata as JSON
if r.status_code != 200:
    print('Something is wrong:',r.content)
else:
    metadata = json.loads(r.text)
    #View metadata:
    print(json.dumps(metadata, indent=2))

