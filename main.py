import asyncio
import re
import json
from createLists import startupCheck, appendFrom, getToken
from game import jeu, MauvaisIndice
import discord
from commandes import weather, randomGifUrl
from datetime import datetime
token = getToken("joshibot")  # either "joshibot" or "testbot"
client = discord.Client()
anagramLock = asyncio.Lock()
aliasLock = asyncio.Lock()



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
        json_data = appendFrom(
            "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2006/04/1-10000",
            "EN", json_data)
        json_data = appendFrom(
            "https://fr.m.wiktionary.org/wiki/Utilisateur:Darkdadaah/Listes/Mots_dump/frwiki/2016-02-03",
            "FR", json_data)
        json_data = appendFrom("http://corpus.rae.es/frec/10000_formas.TXT", "ES", json_data)
        json.dump(json_data, open('liste.json', 'w'), indent=2)
        print("FR : ", len(json_data["FR"]), "EN : ", len(json_data["EN"]), "ES : ", len(json_data["ES"]))

    startupCheck('guilds.json', json.dumps([{}]))
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    for guild in client.guilds:  # checks if any guild/member joined since then

        if str(guild.id) not in json_guilds[0]:
            json_guilds[0][guild.id] = {
                                            "alias":
                                                {
                                                    "prefix": ("!" if token == getToken("testbot") else "<"),
                                                    "weather": "weather",
                                                    "anagramme": "anagramme"

                                                },
                                            "SalonsEtJeuxEnCoursAssocies": {
                                                str(channel.id): 0
                                                for
                                                channel in guild.text_channels},
                                        }

    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)

    startupCheck('members.json', json.dumps(
        {"joueurs": {}}))
    str_data = open('members.json').read()
    json_members = json.loads(str_data)

    for guild in client.guilds:  # checks if any member joined since then
        for member in guild.members:
            if str(member.id) not in json_members["joueurs"]:
                json_members["joueurs"][str(member.id)] = {"XP": 0, "HP":0}


    json.dump(json_members, open('members.json', 'w'), indent=2)



    await client.wait_until_ready()
    await client.change_presence(
        activity=discord.Activity(
            name=f"{len(client.guilds)} servs. Default prefix: " + ("!" if token == getToken("testbot") else "<"),
            type=discord.ActivityType.watching))


@client.event
async def on_member_join(member):
    print(member.id, "est arrivé dans", member.guild.name, "Initialisation de l'XP à zero")
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    if not str(member.id) in json_guilds[0]["joueurs"]:
        json_guilds[0]["joueurs"][str(member.id)] = {"XP": 0, "HP":0}
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
    await client.change_presence(activity=discord.Activity(
        name=f"{len(client.guilds)} servs. Default prefix : " + ("!" if token == getToken("testbot") else "<"),
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
        json_guilds[0][guild.id] = {
            "alias":
                {
                    "prefix": ("!" if token == getToken("testbot") else "<"),
                    "weather": "weather",
                    "anagramme": "anagramme"

                },
            "SalonsEtJeuxEnCoursAssocies": {
                str(channel.id): 0
                for
                channel in guild.text_channels},
        }
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)
    await guild.channels[i].send(
        "Hi {} ! My prefix is '{}'".format(guild.name, json_guilds[0][str(guild.id)]["alias"]["prefix"]))


@client.event
async def on_guild_remove(guild):
    await client.change_presence(
        activity=discord.Activity(
            name=f"{len(client.guilds)} servs. Default prefix : " + ("!" if token == getToken("testbot") else "<"),
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
        json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(channel.id)] = 0
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_guild_channel_delete(channel):
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"].pop(str(channel.id), None)
    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


@client.event
async def on_message(message):
    str_data = open('guilds.json').read()
    json_guilds = json.loads(str_data)
    prefix = json_guilds[0][str(message.guild.id)]["alias"]["prefix"]
    weatherCommand = json_guilds[0][str(message.guild.id)]["alias"]["weather"]
    anagrammeCommand = json_guilds[0][str(message.guild.id)]["alias"]["anagramme"]

    if message.content.startswith(prefix):
        text = message.content[len(prefix):]
        if text.startswith("ca fé peur"):
            if message.author.id == 499302416106258432 or message.author.id == 193424451013050368:
                randomHorrorGif = discord.Embed(color=0xee82ee)
                randomHorrorGif.set_image(url=randomGifUrl("scary"))
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
                    deleted = await message.channel.purge(limit=None)
                    await message.channel.send(str(len(deleted)) + " messages deleted.")
                except discord.errors.Forbidden:
                    await message.channel.send("`403 Forbidden` : Je n'ai pas la permission (errorCode 50013)")

            else:
                await message.channel.send("T'es pas joshinou")

        elif text.startswith(weatherCommand):  # Commande secrète
            await message.channel.send(embed=weather(text))

        elif text.startswith('help'):

            page1 = discord.Embed(
                title="Anagame - Jeu d'anagrammes",
                colour=0x00ff00,
                timestamp=discord.Embed.Empty
            ).add_field(name="Regles du jeu", value="\n   Le bot vous donne un mot mélangé, vous devez deviner duquel il s'agit."
                                                    "Il suffit de répondre avec sa proposition par `%svotreRéponseIci`."
                                                    "\n\n   Les charactères spéciaux (accents, cédilles et autres) seront détéctés"
                                                    " automatiquement, pas besoin de les mettre."
                                                    "Si votre réponse est incorrecte, il la supprime pour que les autres " 
                                                    "joueurs ne la voient pas. Sinon, vous remportez le tour.\n"
                                                    ":star2:Essayez par vous-même !:star2:"%prefix
                        ).add_field(name="Commandes de début de jeu", value=
            ":book: `" + prefix + anagrammeCommand +" ` pour partie simple (1 tour, niveau 1 en FR).\n"
            ":book: `" + prefix + anagrammeCommand + " [niveau] EN/FR/ES [nombre de tours]` pour lancer une partie complète.", inline=True
                                    ).add_field(name="Nota bene", value="\nEn cours de partie, `" + prefix + anagrammeCommand + "` arrête la partie."
            " Le niveau max est `%i` en anglais, `%i` en français, `%i` en espagnol (niveau min 1)." % (
                jeu(1, "EN", 1, 0, {}, []).niveauMax,
                jeu(1, "FR", 1, 0, {}, []).niveauMax,
                jeu(1, "ES", 1, 0, {}, []).niveauMax),
                                  inline=False
                        ).set_author(name="Link to Joshinou's Github", url="https://github.com/charliebobjosh"
                                     ).set_footer(text="Help 1/3", icon_url=client.user.avatar_url
                                                  )
            page2 = discord.Embed(
                title="Alias",
                colour=0x00ff00
            ).add_field(name="Alias", value="Pas encore fini, déso",inline=False
                        ).set_author(name="Link to Joshinou's Github", url="https://github.com/charliebobjosh"
                                     ).set_image(url=message.author.avatar_url
                                                 ).set_footer(text="Help 2/3", icon_url=client.user.avatar_url
                                                              )
            page3 = discord.Embed(
                title='Rien à mettre ici pour le moment...',
                colour=0x00ff00
            ).add_field(name="Rien à voir, circulez...", value="Pas encore fini, déso",inline=False
                        ).set_author(name="Link to Joshinou's Github", url="https://github.com/charliebobjosh"
                                     ).set_footer(text="Help 3/3", icon_url=client.user.avatar_url)

            pages = [page1, page2, page3]

            messageID = await message.channel.send(embed=page1)

            await messageID.add_reaction('\u23ee')
            await messageID.add_reaction('\u25c0')
            await messageID.add_reaction('\u25b6')
            await messageID.add_reaction('\u23ed')

            i = 0
            emoji = ''

            while True:
                if emoji == '\u23ee':
                    i = 0
                    await messageID.edit(embed=pages[i])
                if emoji == '\u25c0':
                    if i > 0:
                        i -= 1
                        await messageID.edit(embed=pages[i])
                if emoji == '\u25b6':
                    if i < 2:
                        i += 1
                        await messageID.edit(embed=pages[i])
                if emoji == '\u23ed':
                    i = 2
                    await messageID.edit(embed=pages[i])

                def check(reaction, user):
                    return reaction.message.id == messageID.id and user != client.user

                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=30, check=check)

                except asyncio.TimeoutError:
                    break

                emoji = str(reaction.emoji)
                await messageID.remove_reaction(reaction.emoji, user)

            await messageID.clear_reactions()

        elif text == "stop":
            if message.author.id == 499302416106258432:
                await message.channel.send("Je vais faire un somme.")
                await client.close()
            else:
                await message.channel.send("T'es pas joshinou")


    async with aliasLock:
        str_data = open('guilds.json').read()
        json_guilds = json.loads(str_data)
        prefix = json_guilds[0][str(message.guild.id)]["alias"]["prefix"]

        if message.content.startswith(prefix+"alias "):
            text = message.content[len(prefix+"alias "):]
            print("commande à changer :",text.split()[0])
            print(text.split()[0]+" in json_guilds[0][str(message.guild.id)][\"alias\"] : ",text.split()[0] in json_guilds[0][str(message.guild.id)]["alias"])
            if text.split()[0] in json_guilds[0][str(message.guild.id)]["alias"]:
                text = text.split()

                json_guilds[0][str(message.guild.id)]["alias"][text[0]] = text[1]
                await message.channel.send(
                    text[0]+" : '%s'" % text[1])
                print(text)
            else:
                await message.channel.send("%s ? Commande inconnue ou inchangeable" % text[0])

        json.dump(json_guilds, open('guilds.json', 'w'), indent=2)

    # print(asyncio.get_running_loop(), "is trying to acquire anagramLock")
    async with anagramLock:  # prevents race conditions. Is probably going to
        # make bot really slower if an alternative
        # isn't found and there's multiple servers
        # using Joshibot.
        # print(asyncio.get_running_loop(), "has acquired anagramLock")
        # solution : make different Locks for different actions
        str_data = open('guilds.json').read()
        json_guilds = json.loads(str_data)

        prefix = json_guilds[0][str(message.guild.id)]["alias"]["prefix"]
        anagrammeCommand = json_guilds[0][str(message.guild.id)]["alias"]["anagramme"]

        if message.content.startswith(prefix):
            text = message.content[len(prefix):]
            attributs = json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)]

            if attributs != 0:
                j = jeu(int(attributs[0]), attributs[1], int(attributs[2]), int(attributs[3]), attributs[4],
                        attributs[5])
            else:
                j = 0

            if j != 0:
                if text.startswith(anagrammeCommand):  # fin de jeu
                    j.nbTours = j.tourNumero
                    await j.prochainTourOuFin(message)

                essai = j.decode(text)
                if essai == j.decode(j.mot) or essai == 'abandon':
                    if essai == j.decode(j.mot):
                        await message.add_reaction("😄")
                    else:
                        await message.add_reaction("😢")

                    name = str(message.author.id)
                    if not name in j.scores:
                        j.scores[name] = 0
                    j.scores[name] += 10 * j.niveau
                    print(j.scores)
                    leaderboard = '\n'.join(
                        ["%s : %i point%s" % (message.guild.get_member(user_id=int(k)).display_name, j.scores[k], ("s" if j.scores[k] > 1 else "")) for k in j.scores])


                    embed = discord.Embed(title="Le mot était \"%s\"" % j.mot,
                                          url="https://" + (j.langue.lower()) + ".m.wiktionary.org/wiki/" + j.mot,
                                          color=0x00ff00)
                    if len(leaderboard) > 0:
                        embed.add_field(name="Leaderboard", value=leaderboard, inline=False)

                    await message.channel.send(embed=embed)

                    await j.prochainTourOuFin(message)
                else:
                    await message.channel.delete_messages([message])



            else:

                if text.startswith(anagrammeCommand):
                    erreur = False
                    try:
                        textList = re.findall(anagrammeCommand+'(?:s)?(.*)', text)[0].split()
                    except:
                        await message.channel.send("Mauvaise saisie")
                        erreur = True
                    if not erreur and len(textList) == 0:
                        j = jeu(1, "FR", 1, 0, {}, [])
                    elif not erreur and len(textList) == 1:
                        try:
                            j = jeu(1, textList[0].upper(), 1, 0, {},
                                    [])  # Alors le bot lance une partie avec Niveau 1, en FR, à 1 tour
                        except MauvaisIndice:
                            j = jeu(int(textList[0]), "FR", 1, 0, {}, [])
                        except:
                            await message.channel.send(
                                "Mauvaise saisie : ` %s%s [niveau ou EN/FR]`"%(prefix,anagrammeCommand))
                            erreur = True
                    elif not erreur and len(textList) == 3:
                        try:
                            j = jeu(int(textList[0]), textList[1].upper(), int(textList[2]), 0, {}, [])
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True

                    elif not erreur and len(textList) == 3:
                        try:
                            j = jeu(int(textList[0]), textList[1] == 'FR', int(textList[2]), 0, {},
                                    [])
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True
                    else:
                        j = jeu(1, "FR", 1, 0, {}, [])

                    if not erreur:  # bon lancement de début de partie
                        await j.prochainTourOuFin(message)
            json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][
                str(message.channel.id)] = j.getAttributes() if j != 0 else 0
            json.dump(json_guilds, open('guilds.json', 'w'), indent=2)

    # print(asyncio.get_running_loop(), "released anagramLock")


client.run(token)
