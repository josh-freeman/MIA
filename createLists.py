from bs4 import BeautifulSoup
import re
import json
import os
import io
import urllib.request


def printHtml(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    if url.endswith("TXT"):
        mystr=mybytes
    else:
        mystr = mybytes.decode("utf-8")

    fp.close()
    return mystr

def getToken(realOrTest:str):
   str_data = open('tokens.json').read()
   token_data = json.loads(str_data)
   return token_data[realOrTest]

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



def appendFrom(url, langue,json_data):
    html= (langue=="FR" or langue == "EN")
    if html:
        fhandle = printHtml(url)
        soup = BeautifulSoup(fhandle, 'html.parser')
        for j in soup.find_all('table'):
            for i in j.find_all('td'):
                text = i.text
                if not re.search(' ', text) and text.islower() and 1 < len(text) and text.isalpha():
                    json_data[langue].append(text)
                    print("trouvé :", text)
    else:
        for i in str(printHtml(url)).split('\\t'):
            text=i.strip()
            if not re.search(' ', text) and text.islower() and text.isalpha and 1<len(text):
                json_data[langue].append(text)
                print("trouvé :", text)

    json_data[langue].sort(key=len)
    json_data["nbMots "+langue] = len(json_data[langue])
    return json_data
