import requests, uuid, json
import subprocess
import json
import sys

# # Add your key and endpoint
# key = "94eb851764ee46139b7d3c019ab1f9f0"
# endpoint = "https://api.cognitive.microsofttranslator.com/"

# # location, also known as region.
# # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
# location = "eastus"

# path = '/translate'
# constructed_url = endpoint + path
from dotenv import load_dotenv
load_dotenv()

api_key= os.getenv("api_key")

def translate (text):
    # Add your key and endpoint
    key = api_key
    endpoint = "https://api.cognitive.microsofttranslator.com/"

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "eastus"
 
    path = '/translate'
    constructed_url = endpoint + path
    
    params = {
    'api-version': '3.0',
    'from': 'en',
    'to': 'de'
    }

    headers = {
    'Ocp-Apim-Subscription-Key': key,
    # location required if you're using a multi-service or regional (not global) resource.
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json'
    }
    # Create the request body
    body = [{'text': text}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    json_data = json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))

    # Save the output JSON to a file
    with open('file.json', 'w') as file:
        file.write(json_data)


# # You can pass more than one object in body.
# body = [{
#     'text': 'I would really like to drive your car around the block a few times!'
# }]



# request = requests.post(constructed_url, params=params, headers=headers, json=body)
# response = request.json()

# json_data = json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))

# # Save the output JSON to a file
# with open('output.json', 'w') as file:
#     file.write(json_data)