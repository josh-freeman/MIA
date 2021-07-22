#for weather
import datetime
import requests
import discord

#for cafaitpeur
import urllib.request, json
from random import choice


def randomGifUrl(search):
    data = json.loads(urllib.request.urlopen(
        "http://api.giphy.com/v1/gifs/search?q="+search+"&api_key=n50bkKdN6ZQdr6wsKjvzHDBcTN1Sx9Is&limit=200").read())
    try:
        return choice(data["data"])["images"]["downsized_large"]["url"]
    except:
        return data["message"]

async def custom_emoji(guild, imageName):
    with open(imageName, "rb") as image:
        f = image.read()
        image = bytearray(f)
    await guild.create_custom_emoji(name="Test", image=image, reason="For fun")

def weather(text):
    api_key = "7fa29540945b8ce7e5b329b5b5497def"
    lst = text.split(" ", text.count(" "))
    if len(lst) == 2:
        ville = lst[1]
    elif len(lst) == 3:
        ville = lst[1] + " " + lst[2]
    url = "http://api.openweathermap.org/data/2.5/weather?appid=" + api_key + "&q=" + ville
    response = requests.get(url)
    resp_js = response.json()
    if resp_js["cod"] != "404":  #SI la ville existe dans la base de donnée du serveur meteo.
        main = resp_js["main"]
        temperature_kelvin = main["temp"]
        pression_atmos = main["pressure"]
        humidite = main["humidity"]

        meteo = resp_js["weather"]
        description = meteo[0]["description"]
        embed = discord.Embed(
            title='Météo à ' + ville.capitalize(),
            description=':date: Aujourd\'hui, le ' + str(datetime.date.today()) + "  :date:",
            colour=discord.Colour.blue()
        )

        if description == 'overcast clouds':
            description = 'temps assez nuageux, pas de bronzage aujourd\'hui...'
            embed.set_thumbnail(url='https://videohive.img.customer.envatousercontent.com/files/135987809/Image%20Preview.jpg?auto=compress%2Cformat&fit=crop&crop=top&max-h=8000&max-w=590&s=82bef0305e018a34f793bba8a2f0615c')
        elif description == 'broken clouds' or description == 'scattered clouds':
            description = 'nuages brisés, quelques éclaircies par moments'
            embed.set_thumbnail(url='https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/625a747a-061b-477d-958f-a0d6cea9e4cb/dax9bd4-dd0da73d-5b6e-415c-b05e-19471f366e5a.jpg/v1/fill/w_1024,h_768,q_75,strp/broken_clouds_by_kevintheman_dax9bd4-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3siaGVpZ2h0IjoiPD03NjgiLCJwYXRoIjoiXC9mXC82MjVhNzQ3YS0wNjFiLTQ3N2QtOTU4Zi1hMGQ2Y2VhOWU0Y2JcL2RheDliZDQtZGQwZGE3M2QtNWI2ZS00MTVjLWIwNWUtMTk0NzFmMzY2ZTVhLmpwZyIsIndpZHRoIjoiPD0xMDI0In1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.TJXNCUYtz9ZqbY1dXZAM190Palxw0hUAwzxks6t4w_M')
        elif description == 'few clouds':
            description = 'plutôt ensoleillé, toutefois quelques nuages peuvent venir et vous passer le bonjour'
            embed.set_thumbnail(url='https://live.staticflickr.com/8145/7158312491_f852e6f1c1_b.jpg')
        elif description == 'clear sky':
            description = 'Ciel dégagé, soleil toute la journée, bref, profite!'
            embed.set_thumbnail(url='https://www.softwareheritage.org/wp-content/uploads/2017/12/clearsky.png')
        elif description == 'light rain':
            description = 'Pluie légère, n\'hésite pas à sortir le parapluie'
            embed.set_thumbnail(url='https://www.dailynews.com/wp-content/uploads/2018/04/ldn-l-weather-rain-dc-11.jpg')
        elif description == 'moderate rain':
            description = 'Temps pluvieux, n\'hésite pas à sortir le parapluie'
            embed.set_thumbnail(url='https://www.dailynews.com/wp-content/uploads/2018/04/ldn-l-weather-rain-dc-11.jpg')
        embed.add_field(name='🌡️ Température en Celsius : ',
                        value=str(round(float(temperature_kelvin) - 273.15, 2)) + " C°", inline=False)
        embed.add_field(name='🌡️ Température en Kelvin : ', value=str(temperature_kelvin) + " K",
                        inline=False)
        embed.add_field(name='Pression atmosphérique in hPa : ', value=str(pression_atmos) + " hPa",
                        inline=False)
        embed.add_field(name=':droplet: Humidité en % :droplet:  ', value=str(humidite) + " %")
        embed.add_field(name='🔸Description🔸 ', value=str(description))
        return embed
    else:
        return " Mais mon cher extraterrestre, cette ville n'est pas sur Terre! "
