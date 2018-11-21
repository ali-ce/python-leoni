import requests
from lxml import html
import pandas as pd
import matplotlib.pyplot as plt

url  = "https://it.wikipedia.org/wiki/Leone_d'oro_al_miglior_film"

#Parse html
response = requests.get(url)
root = html.fromstring(response.text) 

#Naviga root fino alle cell con solo i film, escludendo gli anni senza film. Tutti i film sono in italics, ergo:
films = root.xpath("//th[contains(., 'Anno')]/ancestor::table/tbody/tr/td/i[1]")

#inizia una empty list a cui si aggiungeranno i dictionary
data = []

for film in films:
    tree = root.getroottree() #salva root element
    film_xpath = tree.getpath(film) #store xpath specifica al film in questione, usala poi per spostarti di due colonne e prendere nazioni
    nazioni = [nazione.strip() for nazione in root.xpath(film_xpath+'/ancestor::td/following-sibling::td[2]')[0].text_content().split('/')]
    
    #crea dictionary per ogni nazione_singola-film-regista-anno
    for nazione in nazioni:
        row = {}
        row['nazione'] = nazione
        row['film'] = film.text_content().strip()
        
        #Se anno non è numero (nel caso in cui 2 film hanno vinto in un anno) conversione a testo non funziona e ti lancia un ValueError che puoi sfruttare per sistemare la cosa mettendo come anno quello del row precedente
        try:
            row['anno'] = int(root.xpath(film_xpath+'/ancestor::tr/td')[0].text_content().strip())
        except ValueError:
            row['anno'] = data[-1]['anno']
        
        row['regista'] = root.xpath(film_xpath+'/ancestor::td/following-sibling::td')[0].text_content().strip()
        totale_nazioni = len(nazioni)
        row['prize_share'] = round(1/len(nazioni),2)
        data.append(row)

#Crea dataframe da list of dict
df = pd.DataFrame(data)

#Crea pivot e salva csv
nazioni_count = df.pivot_table(index = 'nazione', aggfunc = {'nazione':'count', 'prize_share':'sum'}).sort_values(by= 'nazione', ascending=False)
nazioni_count.columns = ['leoni_absolute', 'leoni_prize_share'] 
nazioni_count.to_csv('leoni.csv',  encoding='utf8')

# Crea bar e salva
nazioni_count.plot(kind='barh',figsize=(10,10), width=0.8, color=['#5ab4ac','#d8b365']).invert_yaxis()
plt.savefig('leoni.png')