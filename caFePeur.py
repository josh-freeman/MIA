import urllib.request, json
from random import choice


def randomGifUrl(search):
    data = json.loads(urllib.request.urlopen(
        "http://api.giphy.com/v1/gifs/search?q="+search+"&api_key=n50bkKdN6ZQdr6wsKjvzHDBcTN1Sx9Is&limit=20").read())
    return choice(data["data"])["images"]["downsized_large"]["url"]