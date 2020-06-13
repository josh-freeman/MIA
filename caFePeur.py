import urllib.request, json
from random import choice

data=json.loads(urllib.request.urlopen("http://api.giphy.com/v1/gifs/search?q=horror&api_key=n50bkKdN6ZQdr6wsKjvzHDBcTN1Sx9Is&limit=20").read())

def randomGifUrl():
    return choice(data["data"])["images"]["downsized_large"]["url"]