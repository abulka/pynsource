import requests                      # Listing 1
from urllib.parse import urlencode

def find_definition(word):
    q = 'define ' + word
    url = 'http://api.duckduckgo.com/?'
    url += urlencode({'q': q, 'format': 'json'})
    print(url)
    response = requests.get(url)     # I/O
    print(response.status_code)
    data = response.json()           # I/O
    print(data)
    definition = data['Definition']
    if definition == '':
        raise ValueError('that is not a word')
    return definition

find_definition("cat")
