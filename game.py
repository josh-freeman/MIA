import json
import random
from typing import Dict
from unidecode import unidecode as decode
import discord


client = discord.Client()


class MauvaisIndice(Exception):
    pass


class jeu:
    json_data = None
    langue = "FR"
    niveauMax = 0
    niveau = 0
    dicoNiveaux: Dict[str, int] = {"niveau": "indiceMax"}
    listeMots = []
    motsJusqueLa = []
    nbTours = 1
    scores = {"joueur": "score"}
    tourNumero = 0
    mot: str

    def decode(self, mot):
        return decode(mot).lower()

    def setJsonData(self):
        str_data = open('liste.json').read()
        self.json_data = json.loads(str_data)

    async def prochainTourOuFin(self, message):
        if self.tourNumero < self.nbTours:
            embed = discord.Embed(title="Recherche d'un nouveau mot pas encore donné...", color=0xff0000)
            await message.channel.send(embed=embed)
            self.pickword()
            print("nouveau mot : ",self.mot)
            motMelange = self.shuffledWord(self.mot)
            embed = discord.Embed(title="Mot : %s" % motMelange,
                                  description="Tour %i/%i" % (self.tourNumero + 1, self.nbTours), color=0xff0000)
            await message.channel.send(embed=embed)


        else:  #fin du jeu
            self.scores = {k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)}

            embed = discord.Embed(title="Fin de jeu", description=str(self.tourNumero) + str(
                "ème" if self.tourNumero != 1 else "er") + " tour écoulé", color=0x4169e1)
            if len(self.scores) > 0:
                v = list(self.scores.values())
                print(v)
                maxScore = max(v)
                print(self.scores)
                print("maxScore : ", maxScore)

                for i in self.scores:
                    embed.add_field(name=(":crown: " if self.scores[i] == maxScore else "") + "%s" % i,
                                    value=str(self.scores[i]) + " Point" + ("s" if self.scores[i] != 1 else ""),
                                    inline=True)
            else:
                embed.add_field(name="Pas de gagnant...", value="Oups", inline=True)
            await message.channel.send(embed=embed)
        self.tourNumero += 1


    def getAttributes(self):
        return [self.niveau, self.langue, self.nbTours, self.tourNumero, self.scores, self.motsJusqueLa] if self.tourNumero <= self.nbTours else 0
    def __init__(self, niveau, langue, nbTours, tourNumero, scores, motsJusqueLa):
        self.setJsonData()
        self.langue=langue
        self.setNiveauMax()
        self.setNiveau(niveau)
        self.nbTours = nbTours
        self.scores = scores
        self.tourNumero = tourNumero
        self.motsJusqueLa = motsJusqueLa
        self.mot = motsJusqueLa[len(motsJusqueLa)-1]

    def leaderboard(self):
        return self.scores


    def shuffledWord(self, word):
        melange = ''.join(random.sample(word, len(word)))
        return self.shuffledWord(melange) if melange == word else melange

    def setNiveauMax(self):
        self.niveauMax = self.json_data["nbMots "+self.langue] // 450
        self.listeMots = self.json_data[self.langue]
        for i in range(self.niveauMax):
            self.dicoNiveaux[self.niveauMax - i] = len(self.listeMots) // (i + 1)

    def pickword(self):
        mot = random.choice(self.listeMots)
        if mot in self.motsJusqueLa:
            self.pickword()
        else:
            self.motsJusqueLa.append(mot)
            self.mot = mot

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

    def addPlayer(self, nom):
        self.scores[nom] = 0
