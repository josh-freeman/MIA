import asyncio
import re
import json
from createLists import startupCheck, appendFrom, getToken
from game import jeu, MauvaisIndice
import discord
from commandes import weather, randomGifUrl

token = getToken("joshibot") #either "joshibot" or "testbot"
client = discord.Client()
lock = asyncio.Lock()
default_prefix="<"

async def partieProMessage(j: jeu, message):
    embed = discord.Embed(title="Partie pro lancée", color=0x00ff00)
    embed.add_field(name="Statistiques : ", value=str(j), inline=False)
    await message.channel.send(embed=embed)


@client.event
async def on_ready():
    check = startupCheck('liste.json', json.dumps({"FR": [], "EN": [], "ES": []}))
    str_data = open('liste.json').read()
    json_data = json.loads(str_data)
    if not check:
        appendFrom(
            "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2006/04/1-10000",
            "EN", json_data)
        appendFrom("https://fr.m.wiktionary.org/wiki/Utilisateur:Darkdadaah/Listes/Mots_dump/frwiki/2016-02-03",
                   "FR", json_data)
        appendFrom("http://corpus.rae.es/frec/10000_formas.TXT", "ES", json_data)
        print("FR : ", len(json_data["FR"]), "EN : ", len(json_data["EN"]), "ES : ", len(json_data["ES"]))


    startupCheck('guilds.json', json.dumps([{}]))
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    await client.wait_until_ready()
    await client.change_presence(activity=discord.Activity(name=f"{len(client.guilds)} servs. def Prefix: {default_prefix}",
                                                           type=discord.ActivityType.watching))
    json_guilds[0]["joueurs"] = {}
    for guild in client.guilds:

        if str(guild.id) not in json_guilds[0]:
            json_guilds[0][guild.id] = {"prefix": ("!" if token == getToken("testbot") else "<"),
                                        "SalonsEtJeuxEnCoursAssocies": {
                                            channel.id: jeu(1, "FR", 1, 0, {}, False, False, False, [""]).getAttributes()
                                            for channel in guild.text_channels},
                                        }
            for member in guild.members:
                if not member.id in json_guilds[0]["joueurs"]:
                    json_guilds[0]["joueurs"][member.id] = {"XP": 0}

    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_member_join(member):
    print(member.id, "est arrivé dans", member.guild.name, "Initialisation de l'XP à zero")
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    if not member.id in json_guilds[0]["joueurs"]:
        json_guilds[0]["joueurs"][member.id] = {"XP": 0}
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_member_remove(member):
    print(member.id, "est parti de ", member.guild.name, "\neffacement de son XP")

    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    json_guilds[0]["joueurs"].pop(str(member.id), None)
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_guild_join(guild):
    await client.change_presence(activity=discord.Activity(name=f"{len(client.guilds)} servs. Default Prefix: {default_prefix}",
                                                           type=discord.ActivityType.watching))
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    i = 0
    while True:
        if isinstance(guild.channels[i], discord.TextChannel):
            break
        else:
            i += 1

    if guild.id not in json_guilds[0]:
        json_guilds[0][guild.id] = {"prefix": "<",
                                    "SalonsEtJeuxEnCoursAssocies": {
                                        channel.id: jeu(1, "FR", 1, 0, {}, False, False, False, [""]).getAttributes() for
                                        channel in guild.text_channels},
                                    }
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)
    await guild.channels[i].send("Coucou '{}'<".format(guild.name))
    await guild.channels[i].send("Bien réveillé")


@client.event
async def on_guild_remove(guild):
    await client.change_presence(
        activity=discord.Activity(name=f"{len(client.guilds)} servs. Prefix : {default_prefix}",
                                  type=discord.ActivityType.watching))
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    json_guilds[0].pop(str(guild.id), None)
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_guild_channel_create(channel):
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    if str(channel.id) not in json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"]:
        json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(channel.id)] = [
            1,
            "FR",
            1,
            0,
            {},
            False,
            False,
            False,
            ""
        ]
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_guild_channel_delete(channel):
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"].pop(str(channel.id), None)
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)








@client.event
async def on_message(message):
    # print(asyncio.get_running_loop(), "is trying to acquire lock")
    async with lock:  # prevents race conditions. Is probably going to
        # make bot really slower if an alternative
        # isn't found and there's multiple servers
        # using Joshibot.
        # print(asyncio.get_running_loop(), "has acquired lock")
        str_data = open('guilds.json').read()
        json_guilds = json.loads(str_data)

        prefix = json_guilds[0][str(message.guild.id)]["prefix"]

        attributs = json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)]

        j = jeu(int(attributs[0]), attributs[1], int(attributs[2]), int(attributs[3]), attributs[4], attributs[5],
                attributs[6], attributs[7], attributs[8])
        if message.content.startswith(prefix):
            text = message.content[1:]

            if text.startswith("ca fé peur"):
                if message.author.id == 499302416106258432 or message.author.id == 193424451013050368:
                    randomHorrorGif = discord.Embed(color=0xee82ee)
                    randomHorrorGif.set_image(url=randomGifUrl("horreur"))
                    await message.channel.send(embed=randomHorrorGif)
                else:
                    await message.channel.send("Tu n'est pas Joshinou ou Yehlowinou, àbgebundeni bluetwurscht... ")

            elif text.startswith("pikachu"):
                if message.author.id == 499302416106258432 or message.author.id == 330438546710331413:
                    randomPikaGif = discord.Embed(title="Un pikachu sauvage est apparu !", color=0xee82ee)
                    randomPikaGif.set_image(url=randomGifUrl("pikachu"))
                    await message.channel.send(embed=randomPikaGif)
                else:
                    await message.channel.send("¯\_(ツ)_/¯")


            elif text.startswith("delete all messages."):
                if message.author.id == 499302416106258432:
                    try:
                        deleted = await message.channel.purge()
                        await message.channel.send(len(deleted))
                    except discord.errors.Forbidden:
                        await message.channel.send("`403 Forbidden` : Je n'ai pas la permission (errorCode 50013)")

                else:
                    await message.channel.send("T'es pas joshinou")

            if text.startswith("prefixe "):
                text = text[len("prefixe "):]
                if len(text) == 1:
                    if message.author.id == 499302416106258432:
                        json_guilds[0][str(message.guild.id)]["prefix"] = text
                        await message.channel.send("prefixe : '%s'" % json_guilds[0][str(message.guild.id)]["prefix"])
                        print(text)
                        await client.change_presence(
                            activity=discord.Activity(name=f"{len(client.guilds)} servs. Prefix : \"{text}\"",
                                                      type=discord.ActivityType.watching))
                        default_prefix=text
                    else:
                        await message.channel.send("T'es pas joshinou (pas de permission)")
                else:
                    await message.channel.send("%s ? C'est pas un préfixe, ça, gros beta..." % text)

            if text.startswith("weather"): #Commande secrète, n'est pas sur le Bot officiel pour le moment
                if message.author.id == 358629457025826816:
                    await message.channel.send(embed=weather(text))

            if text.startswith('help'):
                helpMessage = discord.Embed(color=0x00ff00)
                helpMessage.set_author(name="Joshinou", url="https://github.com/charliebobjosh")
                helpMessage.add_field(name="Commandes de base",
                                      value=":ear_with_hearing_aid: `" + prefix + "help` pour help."
                                                                                  "\n:vulcan:  `" + prefix + "prefixe [prefixe]` pour changer de prefixe.",
                                      inline=False)
                helpMessage.add_field(name="Anagame - Jeu d'anagrammes", value=
                ":book: `" + prefix + "anagramme(s) ` pour partie simple (1 tour, niveau 1 en FR).\n"
                                      ":book: `" + prefix + "anagramme(s) [niveau]` pour préciser le niveau (1 tour en FR).\n"
                                                            ":book: `" + prefix + "anagramme(s) [EN/FR/ES]` pour préciser la langue (1 tour, niveau 1).\n"
                                                                                  ":book: `" + prefix + "anagramme(s) [niveau] EN/FR/ES [nombre de tours]` pour lancer une partie pro."
                                                                                                        "\nEn cours de partie,`" + prefix + "anagramme(s) ` arrête la partie."
                                                                                                                                            "\nLe niveau max est `%i` en anglais, `%i` en français, `%i` en espagnol (niveau min 1)." % (
                    jeu(1, "EN", 1, 0, {}, False, False, False, [""]).niveauMax,
                    jeu(1, "FR", 1, 0, {}, False, False, False, [""]).niveauMax,
                    jeu(1, "ES", 1, 0, {}, False, False, False, [""]).niveauMax),
                                      inline=False)
                await message.channel.send(embed=helpMessage)



            elif text == "stop":
                if message.author.id == 499302416106258432:
                    await message.channel.send("Je vais faire un somme.")
                    await client.close()
                else:
                    await message.channel.send("T'es pas joshinou")

            if j.partieEnPrepOuCommencee:
                if text.startswith('anagramme'):
                    j.nbTours = j.tourNumero
                    await j.prochainTourOuFin(message, json_guilds)

                elif j.tourNumero < j.nbTours + 1:
                    essai = j.decode(text)
                    if essai == j.decode(j.mot):

                        await message.add_reaction("😄")
                        name = message.author.name
                        if not name in j.scores:
                            j.scores[name] = 0
                        j.scores[name] += j.niveau * 100

                        leaderboard = '\n'.join(
                            [k + " : %i point" % j.scores[k] + ("s" if j.scores[k] > 1 else "") for k in j.scores])
                        embed = discord.Embed(title="Le mot était \"%s\"" % j.mot,
                                              url="https://" + (j.langue.lower()) + ".m.wiktionary.org/wiki/" + j.mot,
                                              color=0x00ff00)
                        if len(leaderboard) > 0:
                            embed.add_field(name="Leaderboard", value=leaderboard, inline=False)

                        await message.channel.send(embed=embed)

                        j.tourCommence = False
                        await j.prochainTourOuFin(message, json_guilds)




                    elif essai == "abandon":
                        await message.add_reaction("😢")
                        leaderboard = '\n'.join(
                            [k + " : %i point" % j.scores[k] + ("s" if j.scores[k] > 1 else "") for k in j.scores])
                        embed = discord.Embed(title="Le mot était \"%s\"" % j.mot,
                                              url="https://" + (j.langue.lower()) + ".m.wiktionary.org/wiki/" + j.mot,
                                              color=0x00ff00)
                        if len(leaderboard) > 0:
                            embed.add_field(name="Leaderboard", value=leaderboard, inline=False)

                        await message.channel.send(embed=embed)
                        await j.prochainTourOuFin(message, json_guilds)

                    else:
                        await message.add_reaction("😬")


            else:

                if text.startswith('anagramme'):
                    erreur = False
                    try:
                        textList = re.findall('anagramme(?:s)?(.*)', text)[0].split()
                    except:
                        await message.channel.send("Mauvaise saisie")
                        erreur = True
                    j = jeu(1, "FR", 1, 0, {}, False, False, False, [""])
                    if not erreur and len(textList) == 0:
                        j = jeu(1, "FR", 1, 0, {}, False, False, False, [""])
                    elif not erreur and len(textList) == 1:
                        try:
                            j = jeu(1, textList[0].upper(), 1, 0, {}, False, False, False,
                                    [""])  # Alors le bot lance une partie avec Niveau 1, en FR, à 1 tour
                        except MauvaisIndice:
                            j = jeu(int(textList[0]), "FR", 1, 0, {}, False, False, False, [""])
                        except:
                            await message.channel.send(
                                "Mauvaise saisie : ` !anagramme(s) [niveau ou EN/FR]`")
                            erreur = True
                    elif not erreur and len(textList) == 3:
                        try:
                            j = jeu(int(textList[0]), textList[1].upper(), int(textList[2]), 0, {}, False, False, False,
                                    [""])
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True

                    elif not erreur and len(textList) == 3:
                        try:
                            j = jeu(int(textList[0]), textList[1] == 'FR', int(textList[2]), 0, {}, False, False, False,
                                    [""])
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True

                    if not erreur:
                        j.partieEnPrepOuCommencee = True
                        j.partieCommencee = True
                        j.pickword()
                        motMelange = j.shuffledWord(j.mot)
                        embed = discord.Embed(title="Mot : %s" % motMelange,
                                              description="Tour %i/%i" % (j.tourNumero + 1, j.nbTours), color=0xff0000)

                        await message.channel.send(embed=embed)
                        j.tourNumero += 1
                        j.tourCommence = True
            json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][message.channel.id] = j.getAttributes()
            json.dump(json_guilds, open('guilds.json', 'w'), indent=2)

    # print(asyncio.get_running_loop(), "released lock")


client.run(token)
