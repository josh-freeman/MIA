import json
import random
from typing import Dict
from unidecode import unidecode as decode
import discord

token = "NzE5OTA1Mjk0NTk0ODY3MjMw.Xt-OOw.UsZbeoDBxNJZZZpLdvkhs-2Ty2E"
client = discord.Client()
desc = '''Coucou. Je suis le bb de joshinou. Mon préfixe est \'<\'.'''

class MauvaisIndice(Exception):
    pass
class jeu:
    json_data = None
    fr = True
    niveauMax = 0
    niveau = 0
    dicoNiveaux: Dict[str, int] = {"niveau": "indiceMax"}
    listeMots = []
    nbTours = 1
    scores = {"joueur": "score"}
    tourNumero = 0
    tourCommence = False
    partieCommencee = False
    partieEnPrepOuCommencee = False
    mot: str

    def decode(self, mot):
        return decode(mot).lower()

    def setJsonData(self):
        str_data = open('liste.json').read()
        self.json_data = json.loads(str_data)

    def reset(self):
        self.setLangueFrancais(True)
        self.setNiveauMax()
        self.setNiveau(1)
        self.nbTours = 1
        self.scores = {}
        self.tourNumero = 0
        self.tourCommence=False
        self.partieCommencee=False
        self.partieEnPrepOuCommencee=False
        self.mot = ""

    async def prochainTourOuFin(self, message, json_guilds):
        if self.tourNumero < self.nbTours:
            self.mot = self.pickword()
            motMelange = self.shuffledWord(self.mot)
            embed = discord.Embed(title="Mot : %s" % motMelange,
                                  description="Tour %i/%i" % (self.tourNumero + 1, self.nbTours), color=0xff0000)
            await message.channel.send(embed=embed)
            self.tourNumero += 1
            self.tourCommence = True
        else:##fin du jeu
            self.scores={k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1],reverse=True)}

            embed = discord.Embed(title="Fin de jeu",description=str(self.tourNumero) + str("ème" if self.tourNumero != 1 else "er") + " tour écoulé",color=0x4169e1)
            if len(self.scores) >0:
                v = list(self.scores.values())
                print(v)
                maxScore=max(v)
                print(self.scores)
                print("maxScore : ",maxScore)

                for i in self.scores:
                    embed.add_field(name=(":crown: "if self.scores[i]==maxScore else "")+"%s"%i, value=str(self.scores[i])+" Point"+("s"if self.scores[i]!=1 else ""), inline=True)
            else:
                embed.add_field(name="Pas de gagnant...", value="Oups", inline=True)
            await message.channel.send(embed=embed)

            self.reset()


    def getAttributes(self):
        return [self.niveau,self.fr,self.nbTours,self.tourNumero,self.scores,self.tourCommence,self.partieCommencee,self.partieEnPrepOuCommencee,self.mot]

    def __init__(self, niveau, francais, nbTours, tourNumero,scores,tourCommence,partieCommencee,partieEnPrepOuCommencee,mot):
        self.setJsonData()
        self.setLangueFrancais(francais)
        self.setNiveauMax()
        self.setNiveau(niveau)
        self.nbTours = nbTours
        self.scores = scores
        self.tourNumero = tourNumero
        self.tourCommence = tourCommence
        self.partieCommencee = partieCommencee
        self.partieEnPrepOuCommencee = partieEnPrepOuCommencee
        self.mot=mot

    def leaderboard(self):
        return self.scores

    def setLangueFrancais(self, bool):
        self.fr = bool

    def shuffledWord(self, word):
        melange = ''.join(random.sample(word, len(word)))
        return self.shuffledWord(melange) if melange == word else melange

    def setNiveauMax(self):
        self.niveauMax = self.json_data["nbMots FR" if self.fr else "nbMots EN"] // 485
        self.listeMots = self.json_data["FR" if self.fr else "EN"]
        for i in range(self.niveauMax):
            self.dicoNiveaux[self.niveauMax - i] = len(self.listeMots) // (i + 1)

    def pickword(self):
        return random.choice(self.listeMots)

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
                    "FR" if self.fr else "EN", self.nbTours,self.niveau, len(self.listeMots),
                    self.json_data['nbMots '+("FR" if self.fr else "EN")],self.tourNumero)



    def addPlayer(self, nom):
        self.scores[nom] = 0

