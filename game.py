import json
import random
from typing import Dict
from unidecode import unidecode as decode
import discord
from math import floor, log



class MauvaisIndice(Exception):
    pass


def niveau(xp: int):
    return floor((1.1095 * log(1.13216 * xp + 8.45279))-2.35672)  # generated on dcode.com


class jeu:
    langue = "FR"
    niveauMax = 0
    niveau = 0
    dicoNiveaux = {"niveau": "indiceMax"}
    listeMots = []
    listeMotsJeu = []
    nbTours = 1
    scores = {"joueur": "score"}
    tourNumero = 0
    mot: str

    def decode(self, mot):
        return decode(mot).lower()

    def setJsonData(self):
        str_data = open('liste.json').read()
        self.json_data = json.loads(str_data)

    def maxXpForLevel(self, n):  # pour les niveaux d'XP, en commençant par le niveau 1
        if n < 0:
            print("Incorrect input")
        # First Fibonacci number is 0, but we start at 1
        elif n == 0:
            return 100
        # Second Fibonacci number is, but we take two
        elif n == 1:
            return 100
        else:
            return self.maxXpForLevel(n - 1) + self.maxXpForLevel(n - 2)

    async def prochainTourOuFin(self, message):
        print("Tour numero : ", self.tourNumero)

        if self.tourNumero < self.nbTours:
            self.mot = self.listeMotsJeu[self.tourNumero]
            print("nouveau mot : ", self.mot)
            if not isinstance(self, pendu):
                motMelange = self.shuffledWord(self.mot) if len(
                    self.mot) > 2 else self.mot[::-1]
                embed = discord.Embed(title="Mot : %s" % motMelange,
                                      description="Tour %i/%i" % (self.tourNumero + 1, self.nbTours), color=0xff0000)
                await message.channel.send(embed=embed)

            else:
                links = ["https://i.imgur.com/gRRyXyj.png", "https://i.imgur.com/y3vb7zv.png",
                         "https://i.imgur.com/y3vb7zv.png", "https://i.imgur.com/LHo66OT.png",
                         "https://i.imgur.com/Mncr1YQ.png", "https://i.imgur.com/cRS7ehx.png",
                         "https://i.imgur.com/f0N6Xt9.png", "https://i.imgur.com/ugTs74Y.png", "",
                         "https://i.imgur.com/cqjfG7K.png"]
                embed = discord.Embed(title=self.currentTry, color=0xff6347).set_image(
                    url=links[self.essaisRates - 1] if self.essaisRates != 0 else None)
                gameMessage = await message.channel.send(embed=embed)
                self.gameMessageId = gameMessage.id
                for i in range(ord("🇦"), ord("🇦") + 20):
                    await gameMessage.add_reaction(chr(i))





        else:  # fin du jeu
            self.scores = {k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)}

            embed = discord.Embed(title="Fin de jeu", description=str(self.tourNumero) + str(
                "ème" if self.tourNumero != 1 else "er") + " tour écoulé", color=0x4169e1)
            if len(self.scores) > 0:
                str_data = open('members.json').read()
                json_members = json.loads(str_data)

                v = list(self.scores.values())
                print(v)
                maxScore = max(v)
                print(self.scores)

                for i in self.scores:
                    xpToAdd = maxScore if self.scores[i] == maxScore else 0
                    str_data = open('guilds.json').read()
                    json_guilds = json.loads(str_data)
                    prefix = json_guilds[0][str(message.guild.id)]["alias"]["prefix"]
                    embed.set_footer(text="%i XP pour chaque gagnant.\nConsultez votre niveau en tapant %s%s" % (
                        maxScore, prefix, "profile"))
                    print("hiya")
                    embed.add_field(
                        name=(":crown: " if self.scores[i] == maxScore and not isinstance(self,
                                                                                          pendu) else "") + "%s" % message.guild.get_member(
                            user_id=int(i)).display_name,
                        value=str(self.scores[i]) + " Point" + ("s" if self.scores[i] != 1 else ""),
                        inline=True)
                    xp = json_members["joueurs"][i]["XP"] if i in json_members["joueurs"] else 0
                    if i not in json_members["joueurs"]:
                        json_members["joueurs"][i] = {"XP": xpToAdd, "HP": 0}
                    else:
                        json_members["joueurs"][i]["XP"] += xpToAdd
                    currLvl = niveau(json_members["joueurs"][i]["XP"])
                    if niveau(xp) < currLvl:
                        lvlGain = abs(currLvl - niveau(xp))
                        x = "x" if lvlGain > 1 else ""
                        embed.add_field(name="XP",
                            value="Gain de niveau%s : %s gagne %i niveau%s" % (x, message.guild.get_member(
                            user_id=int(i)).display_name, lvlGain, x), inline=False)

                json.dump(json_members, open('members.json', 'w'), indent=2)

            else:
                embed.add_field(name="Pas de gagnant...", value="Oups", inline=True)
            await message.channel.send(embed=embed)
        self.tourNumero += 1

    def getAttributes(self):
        return [self.niveau, self.langue, self.nbTours, self.tourNumero, self.scores,
                self.listeMotsJeu] if self.tourNumero < self.nbTours + 1 else 0

    def __init__(self, niveau, langue, nbTours, tourNumero, scores, listeMotsJeu):
        self.setJsonData()
        self.langue = langue
        self.setNiveauMax()
        self.setNiveau(niveau)
        if listeMotsJeu == []:
            listeMotsJeu = random.sample(self.listeMots, k=nbTours)
            print("Nouvelle partie : ", listeMotsJeu)
        self.nbTours = nbTours
        self.scores = scores
        self.tourNumero = tourNumero
        self.listeMotsJeu = listeMotsJeu
        self.mot = listeMotsJeu[tourNumero - 1]

    def shuffledWord(self, word):
        melange = ''.join(random.sample(word, len(word)))
        return self.shuffledWord(melange) if melange == word else melange

    def setNiveauMax(self):
        self.niveauMax = self.json_data["nbMots " + self.langue] // 450
        self.listeMots = self.json_data[self.langue]
        for i in range(self.niveauMax):
            self.dicoNiveaux[self.niveauMax - i] = len(self.listeMots) // (i + 1)

    def setNiveau(self, niveau):

        if niveau not in range(1, self.niveauMax + 1):
            raise MauvaisIndice('Erreur : niveau demandé pas un entier entre 1 et %i' % self.niveauMax)
        else:
            self.niveau = niveau
            self.listeMots = self.listeMots[self.dicoNiveaux[niveau - 1] if niveau > 1 else 0:self.dicoNiveaux[niveau]]

    def __str__(self):
        return "Langue : %s, Nombre de tours : %s. Niveau : %s. " \
               "\nNombre de mots tirés de la base de donnée :%i/%i. " \
               "Tour numéro %i" % (
                   self.langue, self.nbTours, self.niveau, len(self.listeMots),
                   self.json_data['nbMots ' + self.langue], self.tourNumero)


class pendu(jeu):
    joueur: str
    currentTry: str
    essaisRates: int
    gameMessageId: str

    def getAttributes(self):
        if jeu.getAttributes(self) != 0:
            return jeu.getAttributes(self) + [self.joueur, self.currentTry, self.essaisRates, self.gameMessageId]
        else:
            return 0

    def __init__(self, niveau, langue, nbTours, tourNumero, scores, listeMotsJeu, joueur, currentTry, essaisRates,
                 gameMessageId):
        jeu.__init__(self, niveau, langue, nbTours, tourNumero, scores, listeMotsJeu)
        self.joueur = joueur
        self.currentTry = "_" * len(self.mot) if currentTry == "" else currentTry
        self.essaisRates = essaisRates
        self.gameMessageId = gameMessageId
