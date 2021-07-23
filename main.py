import asyncio
import re
import json
from createLists import startupCheck, appendFrom, getToken
from game import jeu, MauvaisIndice, pendu, niveau
import discord
from commandes import weather, randomGifUrl
from random import randrange

token = getToken("testbot")  # either "joshibot" or "testbot"
client = discord.Client()
anagramLock = asyncio.Lock()
aliasLock = asyncio.Lock()
penduLock = asyncio.Lock()
clickerLock = asyncio.Lock()
clickerEmoji = "✔"


async def partieProMessage(j: jeu, message):
    embed = discord.Embed(title="Partie pro lancée", color=0x00ff00)
    embed.add_field(name="Statistiques : ", value=str(j), inline=False)
    await message.channel.send(embed=embed)


@client.event
async def on_reaction_add(reaction, user):
    async with clickerLock:
        str_data_1 = open('guilds.json').read()
        json_guilds = json.loads(str_data_1)
        testLst = json_guilds[0][str(reaction.message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][
            str(reaction.message.channel.id)][
            "clicker"]
        clickerMsgLst = testLst if testLst is not None else []

        if client.user.id != user.id and reaction.message.id in clickerMsgLst and str(reaction.emoji) == clickerEmoji:
            spltLst = reaction.message.content.split("\n")
            spltLst[0] = str(int(spltLst[0]) + 1)
            string = "\n".join(spltLst)
            await reaction.message.edit(content=string)
            await reaction.message.remove_reaction(reaction.emoji, user)

            if randrange(5) == 0:
                str_data_2 = open('members.json').read()
                tmp = json.loads(str_data_2)
                json_members = tmp["joueurs"]
                if str(user.id) not in json_members:
                    json_members[str(user.id)] = {"XP": 0, "HP": 0}
                notif_message = discord.Embed(color=0xee82ee)
                notif_message.set_thumbnail(url=user.avatar_url)
                notif_message.add_field(name="Gain de point !", value="%s gagne un point d'expérience" % user.name)
                json_members[str(user.id)]["XP"] += 1

                tmp["joueurs"] = json_members
                json.dump(tmp, open('members.json', 'w'), indent=2)
                msg = await reaction.message.channel.send(embed=notif_message)
                await msg.delete(delay=2)

    async with penduLock:
        if ord(reaction.emoji) in [i for i in range(ord("🇦"), ord("🇦") + 26)] and user != client.user:
            str_data = open('guilds.json').read()
            json_guilds = json.loads(str_data)
            attributs = json_guilds[0][str(reaction.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(reaction.channel.id)][
                "pendu"]
            if attributs != 0:
                p = pendu(int(attributs[0]), attributs[1], int(attributs[2]), int(attributs[3]), attributs[4],
                          attributs[5], attributs[6], attributs[7], attributs[8], attributs[9])
            else:
                p = 0

            if p != 0:
                essai = chr(ord(reaction.emoji) - ord("🇦") + ord("a"))
                rate = True

            reaction.remove(user)
            json_guilds[0][str(reaction.guild.id)]["SalonsEtJeuxEnCoursAssocies"][
                str(reaction.channel.id)]["pendu"] = p.getAttributes() if p != 0 else 0
        json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


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
                        "anagramme": "anagramme",
                        "clicker": "clicker",
                        "leaderboard": "leaderboard"

                    },
                "SalonsEtJeuxEnCoursAssocies": {
                    str(channel.id): {"anagramme": 0, "pendu": 0, "clicker": 0}
                    for
                    channel in guild.text_channels},
            }

    json.dump(json_guilds, open('guilds.json', 'w'), indent=2)

    startupCheck('members.json', json.dumps(
        {"joueurs": {}}))

    await client.wait_until_ready()
    await client.change_presence(
        activity=discord.Activity(
            name=f"{len(client.guilds)} servs. Default prefix: " + ("!" if token == getToken("testbot") else "<"),
            type=discord.ActivityType.watching))


@client.event
async def on_member_join(member):
    print(member.id, "est arrivé dans", member.guild.name)


@client.event
async def on_member_remove(member):
    print(member.id, "est parti de ", member.guild.name)


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
                    "anagramme": "anagramme",
                    "clicker": "clicker",
                    "leaderboard": "leaderboard"

                },
            "SalonsEtJeuxEnCoursAssocies": {
                str(channel.id): {"anagramme": 0, "pendu": 0, "clicker": 0}
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
        json_guilds[0][str(channel.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(channel.id)] = {"anagramme": 0,
                                                                                                 "pendu": 0,
                                                                                                 "clicker": 0}
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
    clickerCommand = json_guilds[0][str(message.guild.id)]["alias"]["clicker"]
    leaderboardCommand = json_guilds[0][str(message.guild.id)]["alias"]["leaderboard"]
    LEADERBOARD_LENGTH = 3
    MAX_CLICKER_MSG_LENGTH_PER_CHANNEL = 100

    if message.content.startswith(prefix):
        text = message.content[len(prefix):]

        if text.startswith(leaderboardCommand):
            str_data = open('members.json').read()
            json_members = json.loads(str_data)["joueurs"]
            sorted_json_members = iter({k: v for k, v in
                                        sorted(json_members.items(), key=lambda item: item[1]["XP"],
                                               reverse=True)}.items())
            leaderboard = discord.Embed(color=0xff0000, title="Leaderboard mondial :Top %i" % LEADERBOARD_LENGTH)
            i = 0

            for (k, v) in sorted_json_members:
                a = message.guild.get_member(user_id=int(k))
                if i==0 and a is not None:
                    leaderboard.set_thumbnail(url=a.avatar_url)

                usr = str(k if a is None else a.name)
                leaderboard.add_field(name="#%i : User %s"%(i+1,usr),value="Niveau __%i__ (%i XP)"%(niveau(v["XP"]),v["XP"]),inline=False)
                i += 1
                if i == LEADERBOARD_LENGTH:
                    break
            leaderboard.set_footer(text="si un joueur est extérieur au serveur, seul son ID s'affiche.",icon_url=client.user.avatar_url)

            await message.channel.send(embed=leaderboard)


        elif text.startswith(clickerCommand):
            clickerMsg = await message.channel.send("0\nUne chance sur 5 de gagner un XP à chaque clic.")
            msgIds = json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)][
                "clicker"]
            if msgIds is 0 or msgIds is None:
                json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)][
                    "clicker"] = [clickerMsg.id]
            else:
                if msgIds.len() > MAX_CLICKER_MSG_LENGTH_PER_CHANNEL:
                    del msgIds[:MAX_CLICKER_MSG_LENGTH_PER_CHANNEL/2]
                msgIds.append(clickerMsg.id)
                json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)][
                    "clicker"] = msgIds
            await clickerMsg.add_reaction(clickerEmoji)
            json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


        elif text.startswith("ca fé peur"):
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

        elif text.startswith('profile'):
            str_data = open('members.json').read()
            tmp = json.loads(str_data)
            json_members = tmp["joueurs"]
            print(json_members)
            xp = json_members[str(message.author.id)]["XP"]
            msg = discord.Embed(title="User %s, niveau %i" % (message.author.name
                                                              , niveau(xp))).add_field(name="Regles du jeu",
                                                                                       value="Votre XP :%i" % xp)

            await message.channel.send(embed=msg.set_image(url=message.author.avatar_url)
                                       )

        elif text.startswith('help'):

            page1 = discord.Embed(
                title="Anagame - Jeu d'anagrammes",
                colour=0x00ff00,
                timestamp=discord.Embed.Empty
            ).add_field(name="Regles du jeu",
                        value="\n   Le bot vous donne un mot mélangé, vous devez deviner duquel il s'agit."
                              " Il suffit de répondre avec sa proposition par `%svotreRéponseIci`."
                              "\n\n   Les charactères spéciaux (accents, cédilles et autres) seront détéctés"
                              " automatiquement, pas besoin de les mettre."
                              "Si votre réponse est incorrecte, il la supprime pour que les autres "
                              "joueurs ne la voient pas. Sinon, vous remportez le tour.\n"
                              ":star2:Essayez par vous-même !:star2:" % prefix
                        ).add_field(name="Commandes de début de jeu", value=
            ":book: `" + prefix + anagrammeCommand + " ` pour partie simple (1 tour, niveau 1 en FR).\n"
                                                     ":book: `" + prefix + anagrammeCommand + " [niveau] EN/FR/ES [nombre de tours]` pour lancer une partie complète.",
                                    inline=True
                                    ).add_field(name="Nota bene",
                                                value="\nEn cours de partie, `" + prefix + anagrammeCommand + "` arrête la partie."
                                                                                                              " Le niveau max est `%i` en anglais, `%i` en français, `%i` en espagnol (niveau min 1)." % (
                                                          jeu(1, "EN", 1, 0, {}, []).niveauMax,
                                                          jeu(1, "FR", 1, 0, {}, []).niveauMax,
                                                          jeu(1, "ES", 1, 0, {}, []).niveauMax),
                                                inline=False
                                                ).set_author(name="Pour inviter le bot sur ton serveur",
                                                             url="https://discord.com/oauth2/authorize?client_id=701487692793249833&scope=bot&permissions=536964160"
                                                             ).set_footer(text="Help 1/3",
                                                                          icon_url=client.user.avatar_url
                                                                          )
            page2 = discord.Embed(
                title="Alias - commandes réglables",
                colour=0x00ff00
            ).set_author(name="Link to Joshinou's Github", url="https://github.com/josh-freeman"
                         ).set_footer(text="Help 2/3", icon_url=client.user.avatar_url
                                      )
            for command in json_guilds[0][str(message.guild.id)]["alias"]:
                alias = json_guilds[0][str(message.guild.id)]["alias"][command]
                page2.add_field(name=command, value="Alias actuel : \n" + alias)
            page3 = discord.Embed(
                title='Clicker game',
                colour=0x00ff00
            ).add_field(name="Jeu idle de compteur",
                        value=("Essaie la commande %s%s" % (prefix, clickerCommand)) +
                              "\nAh et juste un truc, pour changer d'alias :`%salias commande raccourci`, "
                              "où \"commande\" est le *titre* de la commande, trouvé en page 2. Aussi, vous pouvez afficher votre profil avec ```%sprofile```" % (
                                  prefix, prefix), inline=False
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

        if message.content.startswith(prefix + "alias "):
            text = message.content[len(prefix + "alias "):]
            print("commande à changer :", text.split()[0])
            print(text.split()[0] + " in json_guilds[0][str(message.guild.id)][\"alias\"] : ",
                  text.split()[0] in json_guilds[0][str(message.guild.id)]["alias"])
            if text.split()[0] in json_guilds[0][str(message.guild.id)]["alias"]:
                text = text.split()

                json_guilds[0][str(message.guild.id)]["alias"][text[0]] = text[1]
                await message.channel.send(
                    "La nouvelle commande pour %s est '%s'" % (text[0], text[1]))
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
            attributs = json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)][
                "anagramme"]

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
                        name = str(message.author.id)
                        if not name in j.scores:
                            j.scores[name] = 0

                        j.scores[name] += 10 * j.niveau

                    else:
                        await message.add_reaction("😢")

                    leaderboard = '\n'.join(
                        ["%s : %i point%s" % (message.guild.get_member(user_id=int(k)).display_name, j.scores[k],
                                              ("s" if j.scores[k] > 1 else "")) for k in j.scores])

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
                        textList = re.findall(anagrammeCommand + '(?:s)?(.*)', text)[0].split()
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
                                "Mauvaise saisie : ` %s%s [niveau ou EN/FR]`" % (prefix, anagrammeCommand))
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
                str(message.channel.id)]["anagramme"] = j.getAttributes() if j != 0 else 0
            json.dump(json_guilds, open('guilds.json', 'w'), indent=2)
            # print(asyncio.get_running_loop(), "released anagramLock")

    async with penduLock:
        str_data = open('guilds.json').read()
        json_guilds = json.loads(str_data)
        prefix = json_guilds[0][str(message.guild.id)]["alias"]["prefix"]
        penduCommand = "pendu"

        if message.content.startswith(prefix):
            text = message.content[len(prefix):]
            attributs = json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][str(message.channel.id)][
                "pendu"]

            if attributs != 0:
                p = pendu(int(attributs[0]), attributs[1], int(attributs[2]), int(attributs[3]), attributs[4],
                          attributs[5], attributs[6], attributs[7], attributs[8], attributs[9])
            else:
                p = 0

            if p != 0:
                if text.startswith(penduCommand):  # fin de jeu
                    essai = p.decode(text[len(penduCommand + ' '):])
                    if essai == p.decode(p.mot) or essai == 'abandon':
                        if essai == p.decode(p.mot):
                            await message.add_reaction("😄")
                            name = str(message.author.id)
                            if not name in p.scores:
                                p.scores[name] = 0

                            p.scores[name] += 10 * p.niveau
                            print(p.scores)

                        else:
                            await message.add_reaction("😢")

                        leaderboard = '\n'.join(
                            ["%s : %i point%s" % (message.guild.get_member(user_id=int(k)).display_name, p.scores[k],
                                                  ("s" if p.scores[k] > 1 else "")) for k in p.scores])

                        embed = discord.Embed(title="Le mot était \"%s\"" % p.mot,
                                              url="https://" + (p.langue.lower()) + ".m.wiktionary.org/wiki/" + p.mot,
                                              color=0x00ff00)
                        if len(leaderboard) > 0:
                            embed.add_field(name="Leaderboard", value=leaderboard, inline=False)

                        await message.channel.send(embed=embed)

                        await p.prochainTourOuFin(message)
                    elif essai == "":
                        p.nbTours = p.tourNumero
                        await p.prochainTourOuFin(message)
                    else:
                        await message.channel.delete_messages([message])



            else:

                if text.startswith(penduCommand):
                    erreur = False
                    try:
                        textList = re.findall(penduCommand + '(?:s)?(.*)', text)[0].split()
                    except:
                        await message.channel.send("Mauvaise saisie")
                        erreur = True
                    if not erreur and len(textList) == 0:
                        p = pendu(1, "FR", 1, 0, {}, [], str(message.author.id), "", 0, "0")
                    elif not erreur and len(textList) == 1:
                        try:
                            p = jeu(1, textList[0].upper(), 1, 0, {},
                                    [])  # Alors le bot lance une partie avec Niveau 1, en FR, à 1 tour
                        except MauvaisIndice:
                            p = jeu(int(textList[0]), "FR", 1, 0, {}, [])
                        except:
                            await message.channel.send(
                                "Mauvaise saisie : ` %s%s [niveau ou EN/FR]`" % (prefix, penduCommand))
                            erreur = True
                    elif not erreur and len(textList) == 3:
                        try:
                            p = pendu(int(textList[0]), textList[1].upper(), int(textList[2]), 0, {}, [],
                                      str(message.author.id), "", 0, "0")
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True

                    elif not erreur and len(textList) == 3:
                        try:
                            p = jeu(int(textList[0]), textList[1] == 'FR', int(textList[2]), 0, {},
                                    [])
                            await partieProMessage(j, message)
                        except MauvaisIndice as inst:
                            await message.channel.send(inst)
                            erreur = True
                    else:
                        p = jeu(1, "FR", 1, 0, {}, [])

                    if not erreur:  # bon lancement de début de partie
                        await p.prochainTourOuFin(message)
            json_guilds[0][str(message.guild.id)]["SalonsEtJeuxEnCoursAssocies"][
                str(message.channel.id)]["pendu"] = p.getAttributes() if p != 0 else 0
            json.dump(json_guilds, open('guilds.json', 'w'), indent=2)


client.run(token)
