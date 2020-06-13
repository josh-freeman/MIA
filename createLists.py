from bs4 import BeautifulSoup
import re
import json
import os
import io
import urllib.request


def printHtml(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()

    return mystr


def startupCheck(filename,s):
    if os.path.exists(filename) and os.access('.', os.R_OK):
        # checks if file exists
        print("Base de donnée '%s' existe et est lisible, on peut passer à la suite."%filename)
        return True

    else:
        print("Base de données '%s' manquante ou illisible, création de celle-ci..."%filename)
        with io.open(os.path.join('.', filename), 'w') as db_file:
            db_file.write(s)
            return False



def appendFrom(url, fr: bool, html: bool,json_data):
    if html:
        fhandle = printHtml(url)
        soup = BeautifulSoup(fhandle, 'html.parser')
        for j in soup.find_all('table'):
            for i in j.find_all('td'):
                text = i.text
                if not re.search(' ', text) and text.islower():
                    if 1 < len(text) and text.isalpha():
                        json_data["FR" if fr else "EN"].append(text)
                        print("trouvé :", text)
        json_data["FR" if fr else "EN"].sort(key=len)
    else:
        for i in printHtml(url).split('\n'):
            text=i
            if not re.search(' ', text) and text.islower():
                if 1 < len(text) and text.isalpha():
                    json_data["FR" if fr else "EN"].append(text)
                    print("trouvé :", text)
    json.dump(json_data, open('liste.json', 'w'), indent=2)
